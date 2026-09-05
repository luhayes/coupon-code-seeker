#!/usr/bin/env python3
"""Generate data/links.json — the map the site uses to monetize outbound links.

    python3 scripts/build_links.py           # write the map
    python3 scripts/build_links.py --check   # fail if it is stale

Merchant pages link to the merchant's real URL, so the links work when someone
reads the page on GitHub. On the live site those links are replaced with the
affiliate URL directly — no redirect hop of our own — and this file says which
links to replace and what destination each carries:

    {"merchants/feniko.md": [
       {"from": "https://feniko.pl", "slug": "feniko", "dest": ""},
       {"from": "https://feniko.pl/pierwsza-pozyczka-za-darmo",
        "slug": "feniko", "dest": "/pierwsza-pozyczka-za-darmo"}
    ]}

The build resolves each entry against `affiliates.yml` — which stays out of this
repository — by substituting `{dest}` in that merchant's tracking template with
the merchant's site plus `dest`, URL-encoded. The final href is the affiliate
URL itself, so the reader goes straight there.

The map exists so the site does not have to reimplement the rule below. If it
did, the two would drift, and a drifted rewrite fails silently — the link still
works, it just stops earning. That is the one failure mode this direction has
that writing a redirect path into the file did not, so it is worth removing.

The rule, applied once, here: a link is monetized when its host matches the
merchant's own `website` host, EXCEPT when the URL looks like a support
destination. Sending someone chasing a refund through an affiliate redirect
earns nothing and is a poor thing to do to a reader mid-problem.
"""
import glob
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "links.json")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
LINK = re.compile(r"\]\((https?://[^)]+)\)")

SUPPORT = (
    "help", "support", "return", "faq", "contact", "policy", "terms",
    "track", "status",
    "aide", "retour", "livraison", "conditions", "mentions", "service-client",
    "pomoc", "kontakt", "regulamin", "zwrot", "reklamacj", "dostawa",
    "hilfe", "versand", "ruckgabe", "ayuda", "envio", "devolucion",
)


def host_of(url):
    return re.sub(r"^https?://", "", url).split("/")[0].lower()


def is_support(url):
    return any(marker in url.lower() for marker in SUPPORT)


def build():
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "merchants", "*.md"))):
        text = open(path, encoding="utf-8").read()
        m = FRONTMATTER.match(text)
        if not m:
            continue
        data = yaml.safe_load(m.group(1)) or {}
        slug, site = data.get("slug"), (data.get("website") or "").rstrip("/")
        if not slug or not site:
            continue
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        entries, seen = [], set()
        for url in LINK.findall(text[m.end():]):
            if url in seen or host_of(url) != host_of(site) or is_support(url):
                continue
            seen.add(url)
            tail = url[len(site):]
            entries.append({"from": url, "slug": slug, "dest": tail})
        if entries:
            out[rel] = entries
    return out


def main():
    data = build()
    text = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != text:
            sys.exit("data/links.json is stale — run: python3 scripts/build_links.py")
        print(f"data/links.json is up to date "
              f"({sum(len(v) for v in data.values())} monetized links)")
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(text)
    print(f"wrote data/links.json — {sum(len(v) for v in data.values())} "
          f"monetized links across {len(data)} pages")


if __name__ == "__main__":
    main()
