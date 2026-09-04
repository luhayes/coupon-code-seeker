# Pique Life — internal notes

Not published. See `_notes/README.md`.

## Verification log

**2026-09-04** — checked against Pique-owned pages only: piquelife.com product and
collection pages, the help centre (shipping policy, discounts & deals, Pique
Rewards, the 90-day guarantee) and the referral pages.

Re-verify monthly. Refresh `last_updated` and `verified_on` on the page each time;
`verified_on` is a claim to readers that someone actually re-checked, so only move
it after a real pass.

## Codes considered and rejected

`PIQUESPECIAL10`, `SPRINGSPREE20`, `MISSYOU672838` — circulating on third-party
aggregators. None could be confirmed against a Pique-owned page, and several of
the sites carrying them simultaneously advertise 45–100% off, which is not
credible. Left off the page.

Standing rule: do not publish a specific code until it has been tested in a live
cart. A dead code costs more reader trust than an empty code slot.

## Pre-publish checklist

- [ ] Add the Pique tracking link to the local (gitignored) `affiliates.yml`
      and set `status: active`. Never put it in `affiliates.example.yml` — that
      file is committed to a public repository.
      Commercial anchors already point at `/go/pique-life`; until the link is set
      the redirect resolves untracked to piquelife.com, so no link is broken.
- [ ] Add the logo asset at `/assets/merchants/pique-life.png`.
- [ ] Re-check the prices in the product table — they move with promotions.

## Link decisions

Help centre and returns-portal links are deliberately left as direct external
links rather than routed through `/go/`. They are support destinations rather
than shopping paths, and sending someone chasing a refund through a redirect
would be a poor experience.
