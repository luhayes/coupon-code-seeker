# `/go/<slug>` — the redirect endpoint

Internal spec. This is the one piece of the monetization path that lives on the
live site rather than in this repository, so it is written down here rather than
being rediscovered later.

Every outbound merchant link in `merchants/*.md` is already written as:

```
https://couponcodeseeker.com/go/<slug>[?to=/path/on/merchant/site]
```

The URL is absolute and final — no build step rewrites it, which is why the same
link is clickable on GitHub and correct on the site. Until this endpoint exists,
those links 404. Building it is the last step to a click actually earning.

## Behaviour

1. **Look up the slug** in `affiliates.yml` (`merchants.<slug>`). Unknown slug →
   `404`. Do not fall back to a guess: a mistyped slug that silently redirects
   somewhere plausible is worse than an error page.
2. **Build the destination**: `fallback` (trailing slash stripped) + the `?to=`
   path, or `fallback` alone when there is no `to`.
3. **If `status: active` and `url` is non-empty**, substitute `{dest}` in `url`
   with the URL-encoded destination and redirect there. A template with no
   `{dest}` is valid — the network does not support deep linking — and redirects
   to the template as written, dropping the deep link.
4. **Otherwise** redirect to the destination directly, untracked. The click earns
   nothing but the reader still reaches the store; a merchant with no programme
   yet must never produce a dead link.
5. Answer with `defaults.redirect_status` (302). It is deliberately temporary:
   the target changes whenever a network or tracking parameter does, and a
   cached 301 would keep sending clicks to a retired link.

`scripts/affiliates.py test <slug> [path]` implements exactly steps 2–4 and
prints the resulting hop. Use it as the reference when writing this, and as the
way to check a new tracking template before it goes live.

## Validating `?to=`

**`to` must be a path on the merchant's own site: it starts with a single `/`
and contains no scheme.** Reject `//evil.example.com`, `https://…`, and anything
with a scheme, with a `400` — or ignore `to` and redirect to the bare fallback.
Following it unchecked turns this into an open redirect, which is a phishing
primitive and a fast way to lose a search ranking and an affiliate account.

`scripts/validate.py` enforces the same rule on every committed page, so the
links this site generates are already clean — but the endpoint is a public URL
and anyone can craft a request to it, so it must check for itself.

## Around the endpoint

- **`rel="sponsored nofollow noopener"`** on every rendered `/go/` anchor.
  Markdown cannot express `rel`, so the site adds it when it renders the page.
  An unmarked paid link is what search engines penalise.
- **`Disallow: /go/` in `robots.txt`**, so crawlers never follow the hop and the
  redirect never accumulates index entries of its own.
- **Do not log the referrer against a person.** Slug plus timestamp is enough to
  see which pages convert.
- **Reload `affiliates.yml` without a deploy** if the host allows it. Reading it
  per request is the property that makes switching networks a one-line edit.
  Environment variables (`AFFILIATE_<SLUG_UPPER_SNAKE>`) are the alternative
  where the host prefers secrets to a file.

## Why a redirect at all, rather than the affiliate URL in the page

Both were considered. The redirect wins on two counts:

- **The tracking URL never enters this repository.** The repo is public. Putting
  affiliate links in the Markdown publishes the network, the account IDs and the
  campaign structure to anyone who reads it, and hands a competitor the whole
  monetization map.
- **A network change is one line.** Tracking templates change more often than
  copy does. Editing `affiliates.yml` beats a find-and-replace across 78 links
  in 17 files, and it takes effect on the next click rather than the next build.

The cost is one extra hop, and a dependency: these links are dead until the
endpoint ships.
