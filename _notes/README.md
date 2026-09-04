# Internal notes

*Editorial and build rules live in [CONTRIBUTING.md](../CONTRIBUTING.md).*

Working notes for the content team, one file per merchant, named `<slug>.md`.

**Nothing in this directory is published.** It exists because these notes used to
live in HTML comments inside `merchants/*.md`, which was a mistake: markdown
renderers pass `<!-- ... -->` straight through into the output HTML, so anything
written there is readable by any visitor via View Source. Keep internal reasoning
here, and keep `merchants/*.md` free of HTML comments — `scripts/validate.py`
enforces that.

What belongs here:

- which merchant-owned pages were checked, so the next re-verification pass can
  retrace the same sources
- offers or codes that were considered and rejected, and why, so the decision is
  not re-litigated every month
- outstanding pre-publish tasks for that merchant

Note that this directory is only hidden from *site visitors*. If the GitHub
repository itself is public, these notes are public too.
