#!/usr/bin/env python3
"""Generate the store directory page from the merchant files.

    python3 scripts/build_directory.py           # write stores.md
    python3 scripts/build_directory.py --check   # fail if stores.md is stale

stores.md is generated in full on every run, so never hand-edit it — edit the
merchant pages and regenerate. --check is for CI: it fails when someone adds a
merchant without rebuilding, which is how a directory silently goes out of date.
"""
import glob
import os
import re
import sys
from datetime import date

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "stores.md")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def load_merchants():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "merchants", "*.md"))):
        m = FRONTMATTER.match(open(path, encoding="utf-8").read())
        if not m:
            continue
        d = yaml.safe_load(m.group(1)) or {}
        if not d.get("slug"):
            continue
        # Offers are stored alongside the page, not inside its frontmatter.
        offers_path = os.path.join(ROOT, "data", "offers", f"{d['slug']}.yml")
        raw = []
        if os.path.exists(offers_path):
            raw = (yaml.safe_load(open(offers_path, encoding="utf-8"))
                   or {}).get("offers") or []
        offers = [o for o in raw
                  if isinstance(o, dict) and o.get("status") == "active"]
        # The headline offer is the one a shopper would use first: the largest
        # percentage saving, else the first active offer.
        def rank(o):
            pct = re.search(r"(\d+)\s*%", str(o.get("discount") or ""))
            return int(pct.group(1)) if pct else -1
        best = max(offers, key=rank) if offers else None
        out.append({
            "slug": d["slug"],
            "name": d.get("name") or d["slug"],
            "categories": d.get("categories") or [],
            "primary": d.get("primary_category"),
            "offer_count": len(offers),
            "best": (best or {}).get("title", ""),
            "verified": str(d.get("verified_on") or ""),
        })
    return out


def load_taxonomy():
    path = os.path.join(ROOT, "taxonomy.yml")
    if not os.path.exists(path):
        return {}
    return (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("categories") or {}


def render(ms):
    today = date.today().isoformat()
    total_offers = sum(m["offer_count"] for m in ms)
    tax = load_taxonomy()
    # Group by primary category only. Grouping by every category a merchant
    # carries put some brands in four of five sections, which made the browse
    # tell a reader nothing.
    by_cat = {}
    for m in ms:
        by_cat.setdefault(m["primary"] or "uncategorised", []).append(m)

    s = "" if len(ms) == 1 else "s"
    desc = (f"Browse all {len(ms)} store{s} tracked on Coupon Code Seeker, with "
            f"{total_offers} verified offers. Every deal is checked against the "
            "merchant's own pages.")[:160]

    L = []
    L.append("---")
    L.append("slug: stores")
    L.append("layout: directory")
    L.append("seo:")
    L.append('  title: "All Stores — Verified Coupons & Deals"')
    L.append(f'  description: "{desc}"')
    L.append(f"merchant_count: {len(ms)}")
    L.append(f"offer_count: {total_offers}")
    L.append(f"generated_on: {today}")
    L.append("generated_by: scripts/build_directory.py")
    L.append("---")
    L.append("")
    L.append("# All Stores")
    L.append("")
    if not ms:
        L.append("No stores published yet.")
        return "\n".join(L) + "\n"

    L.append(f"Every store we track, with {total_offers} currently active "
             f"{'offer' if total_offers == 1 else 'offers'} between them. Offers "
             "are verified against each merchant's own pages — we do not list a "
             "code we have not been able to confirm.")
    L.append("")

    L.append("## Browse by category")
    L.append("")
    def label(slug):
        return (tax.get(slug) or {}).get("name", slug)
    for cat in sorted(by_cat, key=label):
        names = ", ".join(
            f"[{m['name']}](merchants/{m['slug']}.md)"
            for m in sorted(by_cat[cat], key=lambda x: x["name"].lower()))
        L.append(f"**[{label(cat)}](categories/{cat}.md)** — {names}")
        L.append("")

    L.append("## All stores A–Z")
    L.append("")
    L.append("| Store | Best current offer | Offers | Verified |")
    L.append("| --- | --- | --- | --- |")
    for m in sorted(ms, key=lambda x: x["name"].lower()):
        L.append(f"| [{m['name']}](merchants/{m['slug']}.md) | {m['best']} | "
                 f"{m['offer_count']} | {m['verified']} |")
    L.append("")
    L.append(f"*{len(ms)} {'store' if len(ms) == 1 else 'stores'}, "
             f"last rebuilt {today}.*")
    return "\n".join(L) + "\n"


def main():
    content = render(load_merchants())
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        # generated_on moves every day; compare everything else.
        strip = lambda s: re.sub(r"^generated_on: .*$|^\*\d+ stores?, last rebuilt.*$",
                                 "", s, flags=re.M)
        if strip(current) != strip(content):
            sys.exit("stores.md is stale — run: python3 scripts/build_directory.py")
        print("stores.md is up to date")
        return
    open(OUT, "w", encoding="utf-8").write(content)
    n = content.count("\n| [")
    print(f"wrote stores.md — {n} store(s)")


if __name__ == "__main__":
    main()
