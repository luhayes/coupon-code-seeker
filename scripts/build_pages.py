#!/usr/bin/env python3
"""Regenerate the deals table inside each merchant page from its offers file.

    python3 scripts/build_pages.py           # rewrite the tables
    python3 scripts/build_pages.py --check   # fail if any table is stale

The table under a page's "Current <name> deals" heading is derived from
data/offers/<slug>.yml. It used to be typed by hand alongside the data, which
meant two copies of the same facts drifting apart — and once a scheduled job
starts proposing offer changes, a hand-written table would be wrong the moment
it landed.

Only the table is generated. The prose around it — the per-offer subsections,
the honest positioning, the FAQ — stays hand-written, because that is the part
a scraper cannot produce and the reason to read this site at all.

The block is delimited by the heading above it and the next "###" or "---"
below, so no marker is needed in the page. HTML comment markers are deliberately
not used: renderers pass them through into the published page source.
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
# Heading, blank line, then the run of table rows.
TABLE = re.compile(r"(^## (?:Current [^\n]*|[^\n]*terms)$\n\n)((?:\|[^\n]*\n)+)", re.M)
FINANCE = {"finance", "loans"}


def is_finance(data, taxonomy):
    """Finance pages get different column headers.

    A loan is not an offer and its cost is not a discount, so those pages use
    Item/Type rather than Offer/Discount/Code. The editorial distinction is the
    point, not a formatting preference.
    """
    cat = data.get("primary_category")
    seen = set()
    while cat and cat not in seen:
        if cat in FINANCE:
            return True
        seen.add(cat)
        cat = (taxonomy.get(cat) or {}).get("parent")
    return False


def render_table(offers, finance):
    live = [o for o in offers if o.get("status") != "expired"]
    if finance:
        rows = ["| # | Item | Type |", "| --- | --- | --- |"]
        for n, o in enumerate(live, 1):
            rows.append(f"| {n} | {o.get('title','')} | {o.get('label','')} |")
        return "\n".join(rows) + "\n"

    # A Status column replaces Code when nothing carries a code and something is
    # unverified — a reader of those pages needs to know what is unconfirmed
    # more than they need an empty Code column.
    unverified = any(o.get("status") != "active" for o in live)
    any_code = any((o.get("code") or "").strip() for o in live)
    last = "Status" if (unverified and not any_code) else "Code"
    rows = [f"| # | Offer | Type | {last} |", "| --- | --- | --- | --- |"]
    for n, o in enumerate(live, 1):
        # `access` is how the reader actually gets the offer when there is no
        # literal code — "Partner link", "Personal link", "Free card". Dropping
        # it would have been a real loss: LMNT's free Sample Pack attaches
        # through a partner link specifically, and a referral needs a personal
        # one. A code, where one exists, outranks it.
        cell = (o.get("code") or "").strip() or o.get("access") or "No code needed"
        rows.append(f"| {n} | {o.get('title','')} | {o.get('label','')} | {cell} |")
    return "\n".join(rows) + "\n"


def main():
    tax = (yaml.safe_load(open(os.path.join(ROOT, "taxonomy.yml"), encoding="utf-8"))
           or {}).get("categories") or {}
    check = "--check" in sys.argv
    stale, changed = [], []

    for path in sorted(glob.glob(os.path.join(ROOT, "merchants", "*.md"))):
        slug = os.path.basename(path)[:-3]
        text = open(path, encoding="utf-8").read()
        m = FRONTMATTER.match(text)
        data = yaml.safe_load(m.group(1)) if m else {}
        offers_path = os.path.join(ROOT, "data", "offers", f"{slug}.yml")
        if not os.path.exists(offers_path):
            continue
        offers = (yaml.safe_load(open(offers_path, encoding="utf-8"))
                  or {}).get("offers") or []
        table = render_table(offers, is_finance(data, tax))

        hit = TABLE.search(text)
        if not hit:
            stale.append(f"{slug} (no deals table found)")
            continue
        if hit.group(2) == table:
            continue
        if check:
            stale.append(slug)
        else:
            open(path, "w", encoding="utf-8").write(
                text[:hit.start(2)] + table + text[hit.end(2):])
            changed.append(slug)

    if check:
        if stale:
            sys.exit("deals tables stale: " + ", ".join(stale) +
                     "\nrun: python3 scripts/build_pages.py")
        print("all deals tables match their offers files")
        return
    print(f"rewrote {len(changed)} deals table(s)" +
          (": " + ", ".join(changed) if changed else " — all already current"))


if __name__ == "__main__":
    main()
