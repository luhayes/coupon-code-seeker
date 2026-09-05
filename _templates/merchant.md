---
# Merchant landing page template for couponcodeseeker.com
# Copy to merchants/<slug>.md and replace every placeholder.
# Never invent an offer, a code, a price or a policy. If it cannot be traced to
# a merchant-owned page, leave it out or mark status: unverified.
slug: merchant-slug                  # kebab-case, must match the filename
name: Merchant Name
aliases: []                          # other names shoppers search for
website: https://www.example.com     # canonical storefront; the redirect's fallback
logo: /assets/merchants/merchant-slug.png
primary_category: ""                 # exactly one slug from taxonomy.yml
categories: []                       # the primary plus at most 2 secondaries
tags: []
currency: USD
ships_to: []
seo:
  title: "Merchant Name Coupons & Promo Codes — Month YYYY"
  description: "150–160 characters. Lead with the single best offer."
  keywords: []
last_updated: YYYY-MM-DD
verified_on: YYYY-MM-DD
# Offers are NOT defined here — copy _templates/offers.yml to
# data/offers/<slug>.yml. Frontmatter is rendered as a table by GitHub and a
# nested array of offers becomes unreadable inside it.
---

# Merchant Name Coupons & Promo Codes

**Best offer right now:** one sentence naming the strongest live offer.

Two or three sentences: what the merchant sells, who it is for, how it is
positioned on price.

*We may earn a commission when you buy through links on this page. It never
changes the price you pay or which offers we list.*

---

## About Merchant Name

Founding, ownership and what actually differentiates the product. Then a
paragraph of honest positioning — where the brand is strong, where it is
expensive or limited. Readers arrive to decide whether to buy, not only to
grab a code.

### What Merchant Name sells

| Line | Notable products | Typical price |
| --- | --- | --- |
|  |  |  |

> Note that prices are captured as of the verification date and change.

---

## Current Merchant Name deals

| # | Offer | Type | Code |
| --- | --- | --- | --- |
| 1 |  |  |  |

### 1. Offer headline

What it is, exactly who qualifies, what is excluded, and any catch worth
flagging. One subsection per offer, in the same order as the table.

---

## How to use a Merchant Name promo code

1. Add items to the cart at [example.com](https://couponcodeseeker.com/go/merchant-slug).
   Every outbound link takes this form — `.../go/<slug>`, plus `?to=/path` for a
   deep link. Help centres and returns portals stay as direct URLs.
2. Continue to checkout.
3. Enter the code in the discount field before payment.
4. Confirm the discount shows in the order summary.
5. Note the free-shipping threshold, if any.

**Stacking:** state how many codes per order, and which non-code discounts
(subscription, loyalty, credits) still apply alongside.

---

## Store information at a glance

| | |
| --- | --- |
| **Website** |  |
| **Founded** |  |
| **Category** |  |
| **Price range** |  |
| **Free shipping** |  |
| **Standard shipping** |  |
| **Ships to** |  |
| **Returns** |  |
| **Loyalty program** |  |
| **Help center** |  |

---

## Frequently asked questions

**Does Merchant Name have a promo code right now?**

**What is the best way to save at Merchant Name?**

**Does Merchant Name offer a student or military discount?**

**What is Merchant Name's return policy?**

**How long does shipping take?**

---

Internal notes for this merchant go in _notes/<slug>.md, never in an HTML
comment here — comments are passed through into the published page source.
