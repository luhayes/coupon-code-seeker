#!/usr/bin/env python3
"""Validate merchant pages before they ship.

    python3 scripts/validate.py

Checks frontmatter integrity, the offer schema, and that every monetized anchor
resolves against affiliates.yml. Exits non-zero on the first failing file so it
can gate a commit or CI run.
"""
import glob
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
GO_LINK = re.compile(r"\]\(/go/([a-z0-9-]+)(?:\?to=([^)]*))?\)")
OFFER_FIELDS = {"id", "title", "type", "discount", "code", "status", "terms"}
TYPES = {"code", "deal"}
STATUSES = {"active", "unverified", "expired"}

errors = []


def check(path, affiliates):
    rel = os.path.relpath(path, ROOT)

    def err(msg):
        errors.append(f"{rel}: {msg}")

    text = open(path, encoding="utf-8").read()
    m = FRONTMATTER.match(text)
    if not m:
        return err("no YAML frontmatter delimited by --- ... ---")
    raw, body = m.group(1), text[m.end():]

    # A blank line inside frontmatter truncates it in parsers that end the block
    # at the first blank line. Everything below then leaks into the page body and
    # markdown collapses it into one run-on paragraph.
    for i, line in enumerate(raw.split("\n"), start=2):
        if not line.strip():
            return err(f"blank line inside frontmatter at line {i} — "
                       "it truncates the block; remove it")

    if "\t" in raw:
        err("tab character in frontmatter — YAML forbids tabs for indentation")

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        return err(f"invalid YAML: {e}")

    # Templates carry placeholders on purpose, so they get the structural checks
    # above (which is where the frontmatter-truncating blank line is caught) but
    # not the content-completeness ones below.
    is_template = rel.startswith("_templates")

    slug = data.get("slug")
    if not slug:
        err("missing `slug`")
    elif not is_template and slug != os.path.splitext(os.path.basename(path))[0]:
        err(f"slug '{slug}' does not match the filename")

    if "affiliate_url" in data:
        err("`affiliate_url` is not used — put the tracking link in affiliates.yml")

    seo = data.get("seo") or {}
    desc = seo.get("description", "")
    if len(desc) > 160:
        err(f"seo.description is {len(desc)} chars; keep it under 160")
    if not seo.get("title"):
        err("missing `seo.title`")

    offers = data.get("offers") or []
    if not offers and not is_template:
        err("no offers defined")
    seen = set()
    for o in offers:
        if not isinstance(o, dict):
            err(f"offer is not a mapping: {o!r}")
            continue
        oid = o.get("id", "<no id>")
        missing = OFFER_FIELDS - set(o)
        if missing:
            err(f"offer '{oid}' missing field(s): {', '.join(sorted(missing))}")
        if o.get("type") not in TYPES:
            err(f"offer '{oid}' has type '{o.get('type')}'; expected one of {sorted(TYPES)}")
        if o.get("status") not in STATUSES:
            err(f"offer '{oid}' has status '{o.get('status')}'; expected one of {sorted(STATUSES)}")
        if o.get("type") == "code" and not o.get("code"):
            err(f"offer '{oid}' is type 'code' but carries no code")
        if not is_template and not (o.get("terms") or "").strip():
            err(f"offer '{oid}' has empty terms — state exclusions and minimums")
        if oid in seen:
            err(f"duplicate offer id '{oid}'")
        seen.add(oid)

    for link_slug, dest in GO_LINK.findall(body):
        if not is_template and link_slug not in affiliates:
            err(f"/go/{link_slug} has no entry in affiliates.yml")
        if dest and not dest.startswith("/"):
            err(f"/go/{link_slug}?to={dest} is not a same-site absolute path")

    # Markdown renderers pass HTML comments straight through into the published
    # page, where any visitor can read them via View Source. Internal reasoning
    # belongs in _notes/<slug>.md instead.
    if "<!--" in body:
        line = body[:body.index("<!--")].count("\n") + raw.count("\n") + 3
        err(f"HTML comment in page body near line {line} — it ships to the "
            "published page source; move it to _notes/")

    for url in re.findall(r"\]\((https?://[^)]+)\)", body):
        host = re.sub(r"^https?://", "", url).split("/")[0]
        if not is_template and slug and host.replace("www.", "").startswith(
                slug.split("-")[0]) and "help" not in host and "return" not in host:
            err(f"raw storefront link {url} — monetized anchors use /go/{slug}")


def load_affiliates():
    """Real map if it exists locally, otherwise the committed schema.

    Only slugs are read here, and slugs are public anyway — every one of them is
    a live page on the site. The tracking URLs are the sensitive part, and this
    repository is public, so they must never reach a committed file.
    """
    real = os.path.join(ROOT, "affiliates.yml")
    example = os.path.join(ROOT, "affiliates.example.yml")
    path = real if os.path.exists(real) else example
    if not os.path.exists(path):
        errors.append("affiliates.example.yml is missing")
        return {}

    merchants = (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("merchants") or {}

    # A tracking link in a committed file is published to the world the moment it
    # is pushed. Catch it here rather than in someone's scraper.
    try:
        import subprocess
        tracked = subprocess.run(
            ["git", "ls-files", "affiliates.yml", "affiliates.example.yml"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        ).stdout.split()
    except Exception:
        tracked = ["affiliates.example.yml"]

    for name in tracked:
        full = os.path.join(ROOT, name)
        if not os.path.exists(full):
            continue
        data = (yaml.safe_load(open(full, encoding="utf-8")) or {}).get("merchants") or {}
        for slug, cfg in (data or {}).items():
            cfg = cfg or {}
            if (cfg.get("url") or "").strip():
                errors.append(
                    f"{name}: merchant '{slug}' has a tracking url in a committed "
                    "file — this repository is public; move it to the gitignored "
                    "affiliates.yml")
            if (cfg.get("network") or "").strip():
                errors.append(
                    f"{name}: merchant '{slug}' names a network in a committed file")
    return merchants


def main():
    affiliates = load_affiliates()

    paths = sorted(glob.glob(os.path.join(ROOT, "merchants", "*.md")) +
                   glob.glob(os.path.join(ROOT, "_templates", "*.md")))
    for p in paths:
        check(p, affiliates)

    if errors:
        print(f"FAILED — {len(errors)} problem(s):\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    print(f"OK — {len(paths)} file(s) valid")


if __name__ == "__main__":
    main()
