# Contributing

How the content in this repository is built and maintained. If you are here to
find a deal rather than to edit one, [start with the README](README.md).

Each merchant gets a Markdown page — short YAML frontmatter plus a long-form body
written for search and for shoppers deciding whether to buy — and a companion
`data/offers/<slug>.yml` holding its structured deals.

Everything here exists to protect one promise the README makes to readers: **we
do not publish an offer we could not verify.** The validation, the `unverified`
status and the re-check cadence are the machinery behind that sentence.

## Layout

```
merchants/             one file per merchant, named <slug>.md
data/offers/           <slug>.yml — the offers for each merchant
taxonomy.yml           the controlled vocabulary of categories
categories/            generated category pages — do not hand-edit
stores.md              generated directory page — do not hand-edit
_notes/                internal working notes, never published
_templates/            merchant.md and offers.yml — copy these to start
affiliates.example.yml public schema for the /go/<slug> tracking map
affiliates.yml         real tracking links — gitignored, never committed
scripts/validate.py    pre-publish checks
scripts/build_pages.py generates the deals table inside each page
scripts/affiliates.py  manage the local tracking links
assets/merchants/      logos, <slug>.png
```

**This repository is public.** The merchant pages are the product, so they belong
in the open, but nothing that would be handed to a competitor or a scraper goes
in with them — see "Affiliate links" below.

Run `python3 scripts/validate.py` before committing. It exits non-zero on a
problem, so it also works as a pre-commit or CI gate.

## Adding a merchant

1. Copy `_templates/merchant.md` to `merchants/<slug>.md`. The slug is kebab-case and
   must match both the filename and the `slug` field.
2. Research against **merchant-owned pages only** — the store itself, its help center,
   its policy and rewards pages. Coupon aggregators are not sources.
3. Fill in the frontmatter, then the body. Keep the section order in the template so
   pages are comparable across merchants. Record your sources, rejected offers and
   open tasks in `_notes/<slug>.md`.
4. Copy `_templates/offers.yml` to `data/offers/<slug>.yml` and fill in the offers:
   `id`, `title`, `type` (`code`/`deal`), `discount`, `code`, `status`
   (`active`/`unverified`/`expired`) and `terms` on each.
5. Set `last_updated` and `verified_on` to the date you actually checked.
6. Add the slug to `affiliates.example.yml`, put the real link in your local
   `affiliates.yml`, and add the logo before the page goes live.

## Categories

Categories are a **controlled vocabulary** defined in `taxonomy.yml`. A merchant
may only use slugs defined there — `scripts/validate.py` rejects anything else,
which is what stops `Tea & Coffee` and `Coffee & Tea` from both existing a year
from now.

Two levels, no more. A flat list puts a category holding ten merchants beside
one holding a single merchant; a third level splits the inventory too thin to
fill a page.

Every merchant declares:

| Field | Meaning |
| --- | --- |
| `primary_category` | Exactly one slug — where the merchant lives, and what the directory groups it under |
| `categories` | The primary plus at most two secondaries, for cross-listing |

**The primary is what keeps browsing useful.** Before it existed, the directory
grouped by every category a merchant carried, so Four Sigmatic appeared in four
of five sections and no section told a reader anything. Related to that: resist
filing a merchant under a broad umbrella like `health-wellness` as its primary.
A category holding 60% of the inventory is not a category, it is a synonym for
the site.

`scripts/build_categories.py` generates a page per category. Two rules keep the
output clean, both enforced in the generator:

- A category with **no merchants** is skipped rather than published empty. Seed
  a category in `taxonomy.yml` ahead of its content and nothing renders until a
  merchant lands in it.
- A parent whose whole member list comes from a **single child** is skipped too:
  it would be the same table at a second URL, which is thin duplicate content
  and makes a reader click through two levels for nothing. The child is
  canonical. A parent that genuinely aggregates several children — `food-drink`
  over tea, coffee and meal delivery — is published.

Adding a category: define it in `taxonomy.yml` first, with real `seo` fields,
then assign merchants. Tags are separate and deliberately uncontrolled — they
describe attributes, not structure, and nothing navigates by them.

## What is generated, and what is written by hand

| Generated — never hand-edit | Written by hand |
| --- | --- |
| The deals table inside each merchant page | Everything else on the page |
| `stores.md` | `data/offers/<slug>.yml` |
| `categories/*.md` | `taxonomy.yml`, `_notes/*` |

The deals table used to be typed by hand next to the same facts in the offers
file, and the two had already drifted before anyone noticed — different wording
for the same offer on more than a dozen pages. `scripts/build_pages.py` derives
it from the offers file instead, matching on the `## Current <name> deals`
heading and the run of table rows beneath it. No marker is needed in the page,
and HTML comment markers are deliberately not used because renderers pass them
into the published page source.

**The prose stays hand-written.** The per-offer subsections, the honest
positioning, the FAQ — that is the part a scraper cannot produce and the reason
to read this site rather than an aggregator. Only the table is machine-owned.

Three offer fields exist for the table:

| Field | Column | Example |
| --- | --- | --- |
| `label` | Type | `Automatic`, `Guarantee`, `Referral`, `**Cost**` |
| `access` | Code, when no code exists | `Personal link`, `Free card`, `Partner link` |
| `expires_on` | — | Optional ISO date; an active offer past it fails validation |

`access` is not decoration: LMNT's free Sample Pack attaches through a partner
link specifically, and a referral needs a personal one. Collapsing those into
"No code needed" would tell a reader the wrong thing.

Finance pages render `Item | Type` instead of `Offer | Type | Code`, decided
from the merchant's primary category. A loan is not an offer and its cost is not
a discount — the distinction is editorial, not cosmetic.

## Where offers live

Offers go in **`data/offers/<slug>.yml`**, never in the page's frontmatter.

GitHub renders a Markdown file's YAML frontmatter as a table, and an array of
objects inside it collapses into a nested table that is effectively unreadable —
wide, clipped, and impossible to scan. Since this repository is public and people
read the pages here directly, that matters. As its own `.yml` file the identical
data renders as plain highlighted source: one offer per block, one field per
line, diffs that are legible in review.

The site reads the two files together — the page for its metadata and copy, the
offers file for the structured deals. `scripts/validate.py` fails if a merchant
has no offers file, or if `offers` reappears in a frontmatter block.

The frontmatter that remains is deliberately short: identity, taxonomy, SEO and
dates. That keeps the table GitHub draws at the top of each page small enough to
be worth reading.

## Frontmatter gotcha

**Never leave a blank line anywhere inside the frontmatter block.** YAML allows
it, but parsers that end frontmatter at the first blank line will silently
truncate there — every key below it, `offers` included, drops into the page body
as plain text, where markdown collapses the lines into one run-on paragraph. The
page still builds, which is what makes it easy to miss. Use comment lines to
separate sections instead of blank lines. `scripts/validate.py` fails on this.

## Content rules

- **Never invent an offer, a code, a price or a policy.** Anything not traceable to a
  merchant-owned page is either omitted or carries `status: unverified`.
- **Do not publish a code you have not seen work in a live cart.** A dead code costs
  more reader trust than an empty code slot. Prefer code-free offers — subscription
  discounts, shipping thresholds, loyalty and referral programs — which are durable and
  verifiable.
- Discount claims on third-party aggregators are frequently unverifiable. They are
  not sources, whatever figure they advertise.
- Keep HTML comments out of `merchants/*.md`. Renderers pass them through into the
  published page, where visitors can read them in the page source. Internal notes
  go in `_notes/<slug>.md`.
- State exclusions, minimums and new-customer restrictions in the offer `terms`.
- Prices change. Label them with the month captured and re-check on each pass.
- Write the positioning honestly, including where a brand is expensive. The page should
  be useful to someone who ends up not buying.

## Affiliate links

Tracking links never appear in page copy, and never in the repository either.
Monetized anchors point at the internal path **`/go/<slug>`**, which the site
resolves to a real tracking URL at redirect time. Deep link with
`/go/<slug>?to=/path/on/merchant/site`.

Because this repository is public, the map is split in two:

| File | Committed? | Contents |
| --- | --- | --- |
| `affiliates.example.yml` | yes | schema and merchant slugs, empty `url`/`network` |
| `affiliates.yml` | **no**, gitignored | the real tracking URLs |

Use `scripts/affiliates.py` rather than editing the YAML by hand — it writes
only to the gitignored file and will not touch the committed schema:

```
python3 scripts/affiliates.py status                    # who is earning, who is not
python3 scripts/affiliates.py set <slug> "<template>" --network impact
python3 scripts/affiliates.py test <slug> /some/path    # show the resolved URL
python3 scripts/affiliates.py unset <slug>              # back to untracked
```

The `url` is a **template**: put `{dest}` where the destination URL belongs, and
the redirect substitutes the URL-encoded destination — the storefront plus the
`?to=` path on a deep link.

```
https://track.example-network.com/c/12345/678/9999?u={dest}
```

Leave `{dest}` out and every link lands on the tracked homepage, which is the
right choice only if your network does not support deep linking. `set` warns
when the template has no `{dest}`, and `test` prints exactly what a given link
resolves to, so you can confirm a deep link survives before trusting it.

Alternatively, supply the links to the redirect endpoint through environment
variables if your host prefers secrets over a file. The merchant slugs stay public deliberately — each one is
already a live page on the site — but a committed tracking URL would hand
competitors your entire merchant-to-network mapping in one file, and some
affiliate agreements prohibit disclosing terms at all. `scripts/validate.py`
fails if a committed affiliates file has a non-empty `url` or `network`.

```markdown
Add your items to the cart at [piquelife.com](/go/pique-life), choosing
["Subscribe & Save"](/go/pique-life?to=/collections/subs-collection) as you go.
```

Why the indirection rather than pasting the network URL into each link:

- A network switch or a tracking-parameter change is one line in `affiliates.yml`,
  not a find-and-replace across every page that mentions the merchant.
- Pages stay readable in the repo, and reviewers can see what a link means.
- The redirect is the natural place to count clicks per merchant and per anchor.
- Before a link exists, `/go/<slug>` falls back to the plain storefront, so a page
  can ship un-monetized without a single broken link.

Placement matters more than the URL: put the link on meaningful anchor text inside
a sentence people are already reading — the offer name, the product, the CTA — not
on a bare URL in a metadata row. Leave support destinations (help centers, returns
portals) as direct external links.

The redirect endpoint must: send `rel="sponsored nofollow noopener"` on rendered
anchors, return **302** and not 301 so a network change is not cached in browsers,
reject any `?to=` value that is not a same-site absolute path, and be disallowed in
`robots.txt` so `/go/` is never crawled.

Every monetized page carries the one-line commission disclosure near the top. It is
in the template — keep it.

## Maintenance

Re-verify each page monthly: confirm live offers, drop expired ones, refresh prices, and
bump `last_updated` / `verified_on`. A page whose `verified_on` is more than a quarter
stale should be treated as unpublished until rechecked.

## Frontmatter reference

| Field | Notes |
| --- | --- |
| `slug` | kebab-case, matches the filename |
| `name` | display name |
| `aliases` | other names shoppers search for |
| `website` | canonical storefront URL |
| — | no tracking link here; see `affiliates.example.yml` |
| `logo` | `/assets/merchants/<slug>.png` |
| `categories`, `tags` | taxonomy for browse and related-merchant modules |
| `ships_to`, `currency` | shipping scope |
| `seo.title` | ~60 characters, ends with the current month and year |
| `seo.description` | 150–160 characters, leads with the best offer |
| — | offers are not in the frontmatter; see `data/offers/<slug>.yml` |
| `last_updated`, `verified_on` | ISO dates from the last real check |

## Store directory

`stores.md` is the public directory page, generated in full from the merchant
files. Never hand-edit it — add or edit a merchant, then rebuild:

```
python3 scripts/build_pages.py                 # rebuild the in-page deals tables
python3 scripts/build_directory.py             # rebuild stores.md
python3 scripts/build_categories.py            # rebuild categories/*.md
python3 scripts/build_pages.py --check         # CI: fail if stale
python3 scripts/build_directory.py --check
python3 scripts/build_categories.py --check
```

All three run in CI on every push and pull request
(`.github/workflows/validate.yml`), alongside `validate.py` and a check that
`affiliates.yml` never became tracked.

It groups merchants by category, lists them A–Z with their headline offer, and
picks that offer as the highest active percentage discount. Run it as part of
every content change so the directory never drifts from the pages.
