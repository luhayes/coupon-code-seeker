# MUD\WTR — internal notes

Not published. See `_notes/README.md`.

## Verification log

**2026-09-04** — shipping tiers, subscription rate, referral and the 30-day
guarantee confirmed against the MUD\WTR help centre, return policy and terms
pages. Founder and founding year from the brand's own founder-story post.

Re-verify monthly.

## Not captured

Product prices. The pages were written without price figures rather than
carrying over numbers from third-party reviews. Capture list prices for :rise,
:balance, :rest and the starter kit on the next pass and add the price column.

## Worth knowing

MUD\WTR allows a promo code **on top of** subscription pricing at the initial
checkout. That is unusual — most subscription brands block it — and it is
called out in the stacking section because it changes how a first order should
be built.

## Pre-publish checklist

- [ ] Tracking link into the gitignored `affiliates.yml`, set `status: active`
- [ ] Logo at `/assets/merchants/mudwtr.png`
- [ ] Capture product prices

## Naming

The brand styles itself MUD\WTR with a backslash. In YAML frontmatter that
means single-quoted scalars only — a double-quoted `"MUD\WTR"` is an invalid
escape sequence and will fail to parse.
