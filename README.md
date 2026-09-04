# coupon-code-seeker

Merchant landing page content for **couponcodeseeker.com**. Each merchant gets one
Markdown file with YAML frontmatter: structured metadata and offers for the site to
render, plus a long-form body written for search and for shoppers deciding whether to buy.

## Layout

```
merchants/           one file per merchant, named <slug>.md
_notes/              internal working notes, never published
_templates/          merchant.md — copy this to start a new page
affiliates.yml       slug -> tracking link map, resolved by /go/<slug>
scripts/validate.py  pre-publish checks
assets/merchants/    logos, <slug>.png
```

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
4. Set `last_updated` and `verified_on` to the date you actually checked.
5. Add an entry to `affiliates.yml` and the logo before the page goes live.

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

Tracking links never appear in page copy. Monetized anchors point at the internal
path **`/go/<slug>`**, which the site resolves through `affiliates.yml` at redirect
time. Deep link with `/go/<slug>?to=/path/on/merchant/site`.

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
| — | no tracking link here; see `affiliates.yml` |
| `logo` | `/assets/merchants/<slug>.png` |
| `categories`, `tags` | taxonomy for browse and related-merchant modules |
| `ships_to`, `currency` | shipping scope |
| `seo.title` | ~60 characters, ends with the current month and year |
| `seo.description` | 150–160 characters, leads with the best offer |
| `offers[]` | `id`, `title`, `type` (`code`/`deal`), `discount`, `code`, `status` (`active`/`unverified`/`expired`), `terms` |
| `last_updated`, `verified_on` | ISO dates from the last real check |

## Merchants

| Merchant | Page | Verified |
| --- | --- | --- |
| Pique Life | [`merchants/pique-life.md`](merchants/pique-life.md) | 2026-09-04 |
