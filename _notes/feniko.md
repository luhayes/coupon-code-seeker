# Feniko — internal notes

Not published. See `_notes/README.md`.

## This is consumer credit, not retail

Feniko.pl is a Polish chwilówka lender. The page is built to a different
standard from the retail merchants and that is deliberate:

- No "best offer" framing. A loan is not a saving.
- The cost sits **above** the offer, in a warning block, not below it.
- ~299% RRSO on repeat borrowing is carried as its own offer entry so the cost
  is visible wherever offers are rendered, not only in the page body.
- The page names the actual failure mode — refinancing the free first loan with
  a priced second one — and points to free statutory debt advice.

Do not let a future rewrite "optimise" this page toward conversion. If the
monetization ever depends on softening the cost disclosure, the right answer is
to drop the merchant.

## Verified

First loan free at 0% RRSO over 30 or 61 days, no commission or interest if
repaid on time. Subsequent loans ~299% RRSO. Payout from about 15 minutes.
General maximum quoted up to 7,000 zl.

## Unresolved

**The free-loan cap.** Sources quote both 3,000 zl and 5,000 zl and we could not
settle it. The page says so and tells the reader to check Feniko's own page —
rather than printing a number that may send someone to apply for an amount that
is not actually free.

## Compliance

Lending affiliate programmes impose rules on how credit may be advertised.
Before setting `status: active`, check the network's creative requirements and
confirm this page's disclosures satisfy them. Re-check the RRSO figures on every
verification pass — a stale rate on a credit page is a compliance problem, not
just an inaccuracy.

## Market fit

Polish market, PLN, Polish-language search intent — on an English-language site.
Raised with the site owner; see the batch summary.
