# coupon-code-seeker

Merchant landing page content for **couponcodeseeker.com**. Each merchant gets one
Markdown file with YAML frontmatter: structured metadata and offers for the site to
render, plus a long-form body written for search and for shoppers deciding whether to buy.

## Layout

```
merchants/           one file per merchant, named <slug>.md
_templates/          merchant.md — copy this to start a new page
assets/merchants/    logos, <slug>.png
```

## Adding a merchant

1. Copy `_templates/merchant.md` to `merchants/<slug>.md`. The slug is kebab-case and
   must match both the filename and the `slug` field.
2. Research against **merchant-owned pages only** — the store itself, its help center,
   its policy and rewards pages. Coupon aggregators are not sources.
3. Fill in the frontmatter, then the body. Keep the section order in the template so
   pages are comparable across merchants.
4. Set `last_updated` and `verified_on` to the date you actually checked.
5. Fill in `affiliate_url` and add the logo before the page goes live.

## Content rules

- **Never invent an offer, a code, a price or a policy.** Anything not traceable to a
  merchant-owned page is either omitted or carries `status: unverified`.
- **Do not publish a code you have not seen work in a live cart.** A dead code costs
  more reader trust than an empty code slot. Prefer code-free offers — subscription
  discounts, shipping thresholds, loyalty and referral programs — which are durable and
  verifiable.
- Ignore the 45–100%-off claims that circulate on scraper sites. They are noise.
- State exclusions, minimums and new-customer restrictions in the offer `terms`.
- Prices change. Label them with the month captured and re-check on each pass.
- Write the positioning honestly, including where a brand is expensive. The page should
  be useful to someone who ends up not buying.

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
| `affiliate_url` | tracked link; required before publishing |
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
