# levanta-help-live

Internal knowledge-base assistant (a Claude Agent Skill) for **Levanta employees** — support, CS/CSM, product, engineering, sales, marketing, ops, and leadership — answering questions about how Levanta's own product works.

Levanta is the affiliate platform connecting Amazon sellers/brands with creators (Creator Connections, Paid Placements, CPC campaigns, Brand Referral Bonus, Amazon Attribution, Shopify integration, Stripe payouts, commissions, tiers, the Creator/Seller API, and more).

## Live, not snapshotted

This skill reads the live knowledge base at **`knowledge.levanta.io` at answer-time** — there is **no bundled snapshot and no periodic sync**. KB-based answers always reflect the current knowledge base, never a stale copy.

How it works:

1. Fetches the live index at `https://knowledge.levanta.io/llms.txt` to discover the current articles, grouped by collection (Creator Accounts, Seller Accounts, Seller Articles 中文) and sub-collection.
2. Picks the relevant article(s) and fetches them live to read the real content.
3. Answers in the employee's language, quotes exact policy numbers/timelines, and cites its sources.

Because the live index is the source of truth, the skill adapts automatically when Levanta adds, renames, or removes articles — nothing in this repo needs to be regenerated.

For up-to-date trends and current context, the skill also searches connected Claude sources — **Pylon** (support tickets + external KB), **Notion** (internal KB), **Linear** (engineering tickets), and **Slack** (internal conversations) — while the live KB is the canonical reference for official product behavior and policy wording. When sources conflict, the skill prioritizes the most recent by date.

## Contents

| File | Purpose |
|---|---|
| `SKILL.md` | The skill definition: when to use it, how to answer live, routing/language guidance, and things to watch out for. |
| `references/glossary.md` | Approved APAC Chinese terminology for Creator-side and cross-cutting terms. **Bundled on purpose** — this is internal and does not live on `knowledge.levanta.io`, so it's the one reference that stays local. |

There is no build, refresh script, or scheduled job — packaging the skill is just this folder as-is.
