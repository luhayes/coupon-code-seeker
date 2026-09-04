#!/usr/bin/env python3
"""Manage the local affiliate tracking links.

    python3 scripts/affiliates.py status
    python3 scripts/affiliates.py set <slug> "<tracking url template>" [--network impact]
    python3 scripts/affiliates.py test <slug> [/path/on/merchant/site]
    python3 scripts/affiliates.py unset <slug>

Real tracking URLs live in `affiliates.yml`, which is gitignored. This script
only ever writes there — it refuses to touch `affiliates.example.yml`, because
that file is committed to a public repository.

The url is a TEMPLATE. Put `{dest}` where the destination URL belongs:

    https://track.example-network.com/c/12345/678/9999?u={dest}

At redirect time `{dest}` is replaced with the URL-encoded destination — the
merchant's site, plus the `?to=` path when the link is a deep link. If your
network does not support deep linking, leave `{dest}` out entirely and every
link lands on the tracked homepage; that still works, it just loses the deep
link.
"""
import os
import shutil
import sys
from urllib.parse import quote

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL = os.path.join(ROOT, "affiliates.yml")
EXAMPLE = os.path.join(ROOT, "affiliates.example.yml")


def load(path):
    return yaml.safe_load(open(path, encoding="utf-8")) or {}


def ensure_real():
    """Create affiliates.yml from the committed schema on first use."""
    if not os.path.exists(REAL):
        if not os.path.exists(EXAMPLE):
            sys.exit("affiliates.example.yml is missing — cannot seed affiliates.yml")
        shutil.copy(EXAMPLE, REAL)
        print(f"created affiliates.yml from the example schema (gitignored)\n")
    return load(REAL)


def save(data):
    # affiliates.yml is a gitignored local file, so a clean dump is fine here.
    with open(REAL, "w", encoding="utf-8") as fh:
        fh.write("# LOCAL FILE — real tracking links. Gitignored; never commit.\n"
                 "# Managed by scripts/affiliates.py. See CONTRIBUTING.md.\n")
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True,
                       default_flow_style=False, width=100)


def resolve(cfg, defaults, to=None):
    """Reproduce what the redirect endpoint does, so `test` shows the truth."""
    fallback = (cfg.get("fallback") or "").rstrip("/")
    dest = fallback + to if to else fallback
    if cfg.get("status") != "active" or not (cfg.get("url") or "").strip():
        return dest, "untracked fallback (status is not active)"
    url = cfg["url"]
    if "{dest}" in url:
        return url.replace("{dest}", quote(dest, safe="")), "tracked, deep link preserved"
    return url, "tracked homepage (template has no {dest}, deep link dropped)"


def cmd_status():
    data = load(REAL) if os.path.exists(REAL) else load(EXAMPLE)
    merchants = data.get("merchants") or {}
    if not os.path.exists(REAL):
        print("affiliates.yml does not exist yet — showing the schema.\n"
              "Run `set` on any merchant and it will be created.\n")
    active = [s for s, c in merchants.items() if (c or {}).get("status") == "active"]
    width = max([len(s) for s in merchants] + [8]) + 2
    print(f"{'':4}{'merchant':{width}}{'status':14}network")
    print("-" * (width + 32))
    for slug, cfg in merchants.items():
        cfg = cfg or {}
        st = cfg.get("status", "?")
        mark = "OK  " if st == "active" else "    "
        print(f"{mark}{slug:{width}}{st:14}{cfg.get('network') or '-'}")
    print("-" * (width + 32))
    print(f"{len(active)} of {len(merchants)} merchants earning. "
          f"{len(merchants) - len(active)} still resolve untracked to the storefront.")


def cmd_set(slug, url, network=None):
    data = ensure_real()
    merchants = data.setdefault("merchants", {})
    if slug not in merchants:
        sys.exit(f"unknown merchant '{slug}'. Add it to affiliates.example.yml first "
                 f"so the slug is part of the committed schema.")
    if not url.strip():
        sys.exit("empty url")
    cfg = merchants[slug] or {}
    cfg["url"] = url
    cfg["status"] = "active"
    if network:
        cfg["network"] = network
    merchants[slug] = cfg
    save(data)
    print(f"{slug}: tracking link set, status = active")
    if "{dest}" not in url:
        print("\n  NOTE: the template has no {dest}, so every deep link on this\n"
              "  merchant's page will land on the tracked homepage instead of the\n"
              "  product or collection it names. Fine if your network does not\n"
              "  support deep linking — otherwise add {dest} where the destination\n"
              "  URL belongs.")
    defaults = data.get("defaults") or {}
    out, note = resolve(cfg, defaults)
    print(f"\n  /go/{slug}  ->  {out}\n  ({note})")


def cmd_unset(slug):
    data = ensure_real()
    cfg = (data.get("merchants") or {}).get(slug)
    if cfg is None:
        sys.exit(f"unknown merchant '{slug}'")
    cfg["url"] = ""
    cfg["status"] = "unconfigured"
    save(data)
    print(f"{slug}: tracking link cleared — /go/{slug} now falls back untracked")


def cmd_test(slug, to=None):
    path = REAL if os.path.exists(REAL) else EXAMPLE
    data = load(path)
    cfg = (data.get("merchants") or {}).get(slug)
    if cfg is None:
        sys.exit(f"unknown merchant '{slug}'")
    if to and not to.startswith("/"):
        sys.exit("the ?to= path must be a same-site absolute path starting with '/'")
    out, note = resolve(cfg, data.get("defaults") or {}, to)
    label = f"/go/{slug}" + (f"?to={to}" if to else "")
    print(f"source: {os.path.basename(path)}\n\n{label}\n  ->  {out}\n  ({note})")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd = args[0]
    if cmd == "status":
        cmd_status()
    elif cmd == "set":
        if len(args) < 3:
            sys.exit('usage: affiliates.py set <slug> "<url template>" [--network name]')
        network = None
        if "--network" in args:
            i = args.index("--network")
            network = args[i + 1] if len(args) > i + 1 else None
            args = args[:i] + args[i + 2:]
        cmd_set(args[1], args[2], network)
    elif cmd == "unset":
        cmd_unset(args[1])
    elif cmd == "test":
        cmd_test(args[1], args[2] if len(args) > 2 else None)
    else:
        sys.exit(f"unknown command '{cmd}' — try: status, set, test, unset")


if __name__ == "__main__":
    main()
