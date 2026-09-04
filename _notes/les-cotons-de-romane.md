# Les Cotons de Romane — internal notes

Not published. See `_notes/README.md`.

## Domain verification — the important part

Automated reputation scanners disagree sharply on this brand: one scores
lescotonsderomane.com 4/100 with scam markers, another rates it reliable across
127 criteria, and there is a signal-arnaques report under the brand name.

Resolved: **lescotonsderomane.com is the official shop.** The brand promotes
that exact domain in the caption of its own TikTok videos from
@lescotonsderomane (~105k followers), and the matching Instagram account has
~227k. That is the brand speaking from accounts it controls — the strongest
signal available.

The conflicting scores are explained by imitation domains, not by the real shop:
`lescotons.shop` and `lescotonsderomanestore.shop` reproduce the brand's name,
photography and listings. The page carries a prominent warning block naming the
official domain, because sending a reader to a clone is the worst outcome this
site can produce.

**Never set status: active in affiliates.yml until the tracking link has been
confirmed to resolve to lescotonsderomane.com.**

## Confirmed

Romane Gautret, founded 2019, formerly a paediatric nurse, based in Rennes
(workshop at 4 rue de la Sauvaie, has held open-door sales). Sewn range made
in-house. Also sells wholesale via Ankorstore. Contact
lescotonsderomane@gmail.com. GLS is the stated delivery partner.

## Resolved 2026-09-04 — shipping and returns

Both offers that shipped as `unverified` are now confirmed and active, from the
shop's own policy pages:

- **Delivery** — free over €60 within metropolitan France, via GLS. Delivery
  complaints must be raised by email within **14 days** of receipt with
  evidence; after that the goods are treated as accepted.
- **Returns** — approved refunds processed within **14 days** of the seller
  receiving the return. **Return postage is at the buyer's expense** and the
  original delivery charge is not refunded. Proven defects are refunded or
  replaced at the seller's expense.

How this surfaced is worth recording: the monitoring repo's first run failed to
fetch the two Les Cotons URLs, because they were paths I had guessed rather than
looked up. Finding the correct Shopify `/policies/` paths turned up the policy
content itself. **The lesson is the general one — do not guess a URL** — and the
monitoring caught it within a day of shipping.

## Still open

Prices were not captured. The page says so rather than estimating.
