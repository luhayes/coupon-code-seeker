#!/usr/bin/env python3
"""Generate a landing page per category from taxonomy.yml and the merchant files.

    python3 scripts/build_categories.py           # write categories/*.md
    python3 scripts/build_categories.py --check   # fail if any page is stale

Pages are generated in full — never hand-edit them. Edit taxonomy.yml (for the
copy and SEO) or a merchant's primary_category, then rebuild.

A category lists every merchant that carries its slug, and a parent category
also gathers the merchants of its children, so /categories/food-drink covers
tea, coffee and meal delivery without any merchant having to be filed twice.
Categories with no merchants are skipped rather than published empty.
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
OUT_DIR = os.path.join(ROOT, "categories")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def taxonomy():
    return (yaml.safe_load(open(os.path.join(ROOT, "taxonomy.yml"),
                                encoding="utf-8")) or {}).get("categories") or {}


def merchants():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "merchants", "*.md"))):
        m = FRONTMATTER.match(open(path, encoding="utf-8").read())
        if not m:
            continue
        d = yaml.safe_load(m.group(1)) or {}
        if not d.get("slug"):
            continue
        offers_path = os.path.join(ROOT, "data", "offers", f"{d['slug']}.yml")
        raw = []
        if os.path.exists(offers_path):
            raw = (yaml.safe_load(open(offers_path, encoding="utf-8"))
                   or {}).get("offers") or []
        active = [o for o in raw if isinstance(o, dict) and o.get("status") == "active"]

        def rank(o):
            pct = re.search(r"(\d+)\s*%", str(o.get("discount") or ""))
            return int(pct.group(1)) if pct else -1
        best = max(active, key=rank) if active else None
        out.append({
            "slug": d["slug"],
            "name": d.get("name") or d["slug"],
            "categories": d.get("categories") or [],
            "primary": d.get("primary_category"),
            "offers": len(active),
            "best": (best or {}).get("title", ""),
            "verified": str(d.get("verified_on") or ""),
        })
    return out


def members(slug, tax, all_merchants):
    """Merchants in this category, including those in its child categories."""
    wanted = {slug} | {s for s, c in tax.items() if (c or {}).get("parent") == slug}
    return sorted((m for m in all_merchants if wanted & set(m["categories"])),
                  key=lambda m: m["name"].lower())


def render(slug, cfg, rows, tax):
    cfg = cfg or {}
    name = cfg.get("name", slug)
    seo = cfg.get("seo") or {}
    parent = cfg.get("parent")
    children = sorted(s for s, c in tax.items() if (c or {}).get("parent") == slug)
    total = sum(r["offers"] for r in rows)

    L = ["---", f"slug: {slug}", "layout: category", "type: category-page"]
    if parent:
        L.append(f"parent: {parent}")
    L.append("seo:")
    L.append(f'  title: "{seo.get("title", name)}"')
    L.append(f'  description: "{seo.get("description", "")}"')
    L.append(f"merchant_count: {len(rows)}")
    L.append(f"offer_count: {total}")
    L.append(f"generated_on: {date.today().isoformat()}")
    L.append("generated_by: scripts/build_categories.py")
    L.append("---")
    L.append("")
    L.append(f"# {name}")
    L.append("")
    desc = (cfg.get("description") or "").strip()
    if desc:
        L.append(desc)
        L.append("")
    plural = "store" if len(rows) == 1 else "stores"
    L.append(f"{len(rows)} {plural}, {total} active "
             f"{'offer' if total == 1 else 'offers'}. Every offer is checked "
             "against the merchant's own pages — we do not list a code we could "
             "not confirm.")
    L.append("")
    if children:
        L.append("**In this category:** " + ", ".join(
            f"[{(tax[c] or {}).get('name', c)}](/categories/{c})" for c in children))
        L.append("")
    L.append("| Store | Best current offer | Offers | Verified |")
    L.append("| --- | --- | --- | --- |")
    for r in rows:
        L.append(f"| [{r['name']}](/stores/{r['slug']}) | {r['best']} | "
                 f"{r['offers']} | {r['verified']} |")
    L.append("")
    L.append(f"[All stores](/stores)" + (
        f" · [{(tax[parent] or {}).get('name', parent)}](/categories/{parent})"
        if parent else ""))
    return "\n".join(L) + "\n"


def main():
    tax, all_m = taxonomy(), merchants()
    os.makedirs(OUT_DIR, exist_ok=True)
    wanted, stale = {}, []
    for slug, cfg in tax.items():
        rows = members(slug, tax, all_m)
        if not rows:
            continue  # never publish an empty category page
        # Nor one that duplicates its only child. A parent whose entire member
        # list comes from a single child is the same page at a second URL —
        # thin duplicate content, and a reader gains nothing by clicking through
        # two levels to the identical table. The child is the canonical page.
        kids = [c for c in tax if (tax[c] or {}).get("parent") == slug]
        filled = [c for c in kids if members(c, tax, all_m)]
        if len(filled) == 1 and members(filled[0], tax, all_m) == rows:
            continue
        wanted[slug] = render(slug, cfg, rows, tax)

    strip = lambda s: re.sub(r"^generated_on: .*$", "", s, flags=re.M)
    if "--check" in sys.argv:
        for slug, content in wanted.items():
            p = os.path.join(OUT_DIR, f"{slug}.md")
            cur = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
            if strip(cur) != strip(content):
                stale.append(slug)
        extra = {os.path.basename(p)[:-3] for p in glob.glob(os.path.join(OUT_DIR, "*.md"))} - set(wanted)
        if stale or extra:
            sys.exit(f"category pages stale ({', '.join(sorted(stale) + sorted(extra))}) "
                     "— run: python3 scripts/build_categories.py")
        print(f"{len(wanted)} category pages up to date")
        return

    for slug, content in wanted.items():
        open(os.path.join(OUT_DIR, f"{slug}.md"), "w", encoding="utf-8").write(content)
    # remove pages for categories that no longer have merchants
    for p in glob.glob(os.path.join(OUT_DIR, "*.md")):
        if os.path.basename(p)[:-3] not in wanted:
            os.remove(p)
            print(f"removed empty category page: {os.path.basename(p)}")
    print(f"wrote {len(wanted)} category pages")


if __name__ == "__main__":
    main()
