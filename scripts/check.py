#!/usr/bin/env python3
"""Check the repository against the rules in AGENTS.md.

No third-party dependencies. Run from the repository root:

    python3 scripts/check.py

Exits non-zero and lists every problem found.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Files exempt from prose rules: AGENTS.md states the rules, so it contains
# examples of what it forbids.
PROSE_EXEMPT = {"AGENTS.md"}

CASE_STUDY_WORDS = 800
OTHER_WORDS = 1200

CASE_STUDY_SECTIONS = [
    "Summary",
    "How it works",
    "What works",
    "What doesn't",
    "Takeaways",
    "Sources",
]

FILLER = [
    "however", "moreover", "furthermore", "additionally", "ultimately",
    "crucial", "pivotal", "robust", "nuanced", "leverage", "landscape",
    "delve", "underscore", "highlights", "a testament to",
]

META = [
    "this document", "in this section", "as noted above",
    "it's worth noting", "let's look at",
]

SHORTHAND = [
    (r"§\s*\d", "section sign with a number"),
    (r"\bQ-?\d+\b", "Q-number"),
    (r"\bR\d+\b", "R-number"),
    (r"\bJ\d+\b", "J-number"),
]

problems = []


def problem(path, line, msg):
    where = f"{path}:{line}" if line else str(path)
    problems.append(f"{where}: {msg}")


def markdown_files():
    for p in sorted(ROOT.rglob("*.md")):
        if ".git" in p.parts:
            continue
        yield p


def strip_fenced(text):
    """Blank out fenced code blocks, preserving line numbering."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return out


def strip_spans(line):
    """Remove inline code spans and double-quoted text.

    Quotations have to be exact, so a forbidden word inside one is not the
    writer's choice. Code spans may legitimately contain anything.
    """
    line = re.sub(r"`[^`]*`", "", line)
    line = re.sub(r'"[^"]*"', "", line)
    return line


def rel(p):
    return p.relative_to(ROOT).as_posix()


def check_prose(path, lines):
    if path.name in PROSE_EXEMPT:
        return
    for i, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        if "—" in strip_spans(raw):
            problem(rel(path), i, "em dash; use a comma, colon, period, or parentheses")
        clean = strip_spans(raw).lower()
        for word in FILLER:
            if re.search(r"\b" + re.escape(word) + r"\b", clean):
                problem(rel(path), i, f"filler word {word!r}")
        for phrase in META:
            if phrase in clean:
                problem(rel(path), i, f"meta narration {phrase!r}")
        no_code = re.sub(r"`[^`]*`", "", raw)
        for pattern, label in SHORTHAND:
            if re.search(pattern, no_code):
                problem(rel(path), i, f"private shorthand ({label}); name the thing and link it")


def check_size(path, text):
    words = len(text.split())
    limit = CASE_STUDY_WORDS if (
        path.parent.name == "case-studies" and path.name != "README.md"
    ) else OTHER_WORDS
    if words > limit:
        problem(rel(path), None, f"{words} words, limit {limit}; cut before splitting")


def check_filename(path):
    name = path.name
    if name in ("README.md", "AGENTS.md"):
        return
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.md", name):
        problem(rel(path), None, "filename is not kebab-case")


def check_links(path, lines):
    for i, raw in enumerate(lines, 1):
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", raw):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            if not resolved.exists():
                problem(rel(path), i, f"link target missing: {target}")


def check_indexes():
    for readme in sorted(ROOT.rglob("README.md")):
        if ".git" in readme.parts:
            continue
        d = readme.parent
        siblings = sorted(
            p.name for p in d.glob("*.md")
            if p.name not in ("README.md", "AGENTS.md")
        )
        text = readme.read_text()
        linked = set(re.findall(r"\]\(([a-z0-9-]+\.md)\)", text))
        for name in siblings:
            if name not in linked:
                problem(rel(readme), None, f"index is missing {name}")
        for name in sorted(linked):
            if not (d / name).exists():
                problem(rel(readme), None, f"index links {name}, which does not exist")


def check_dirs_have_readme():
    for d in sorted(ROOT.rglob("*")):
        if not d.is_dir() or ".git" in d.parts:
            continue
        if d.name in ("scripts", ".github", "workflows"):
            continue
        if any(d.glob("*.md")) and not (d / "README.md").exists():
            problem(rel(d), None, "directory has markdown files but no README.md index")


def check_case_studies():
    d = ROOT / "case-studies"
    if not d.exists():
        return
    for path in sorted(d.glob("*.md")):
        if path.name == "README.md":
            continue
        found = [h.strip() for h in re.findall(r"^##\s+(.+)$", path.read_text(), re.M)]
        unknown = [h for h in found if h not in CASE_STUDY_SECTIONS]
        for h in unknown:
            problem(rel(path), None, f"unexpected section {h!r}")
        known = [h for h in found if h in CASE_STUDY_SECTIONS]
        expected = [s for s in CASE_STUDY_SECTIONS if s in known]
        if known != expected:
            problem(rel(path), None, f"sections out of order: {known} should be {expected}")


def check_heading(path, lines):
    for line in lines:
        if line.strip():
            if not line.startswith("# "):
                problem(rel(path), 1, "first line is not a level-one heading")
            return


def check_external_links():
    """Verify every external URL resolves. Network-dependent, so opt-in."""
    import urllib.error
    import urllib.request

    urls = {}
    for path in markdown_files():
        for i, raw in enumerate(strip_fenced(path.read_text()), 1):
            for m in re.finditer(r"https?://[^)\s\]>\"']+", raw):
                urls.setdefault(m.group(0).rstrip(".,;"), (rel(path), i))

    print(f"checking {len(urls)} external links")
    for url, (path, line) in sorted(urls.items()):
        req = urllib.request.Request(
            url, headers={"User-Agent": "declarative-modeling-link-check"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status >= 400:
                    problem(path, line, f"{resp.status} {url}")
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429):  # bot protection, not a dead link
                problem(path, line, f"{e.code} {url}")
        except Exception as e:  # noqa: BLE001
            problem(path, line, f"unreachable ({type(e).__name__}) {url}")


def main():
    for path in markdown_files():
        text = path.read_text()
        lines = strip_fenced(text)
        check_filename(path)
        check_size(path, text)
        check_heading(path, lines)
        check_prose(path, lines)
        check_links(path, lines)
    check_indexes()
    check_dirs_have_readme()
    check_case_studies()
    if "--external" in sys.argv:
        check_external_links()

    if problems:
        print(f"{len(problems)} problem(s):\n")
        for p in problems:
            print(f"  {p}")
        print("\nSee AGENTS.md. Cutting is the default fix.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
