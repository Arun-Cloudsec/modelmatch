# Catalog refresh — 21 August 2026

Catalog went from **135 → 145 models**: 18 current models added, 8 retired ones removed.

Every price below was checked against a live vendor source on 21 Aug 2026. Each new
record carries a `verified` field naming its source, so the next person to touch this
can tell what was confirmed and what wasn't.

---

## Added — current frontier lineup

### Anthropic (7)
The catalog had no Claude newer than 3.7 Sonnet. The entire Claude 5 family was missing.

| Model | Price /1M | Context | Note |
|---|---|---|---|
| Claude Fable 5 | $10 / $50 | 1M | Highest-capability Claude available publicly |
| Claude Mythos 5 | $10 / $50 | 1M | Not public — Project Glasswing partners only |
| Claude Opus 5 | $5 / $25 | 1M | Flagship; Fast mode $10/$50 |
| Claude Opus 4.8 | $5 / $25 | 1M | Previous flagship, same price |
| Claude Sonnet 5 | $2 / $10 | 1M | Best price-performance; released 30 Jun 2026 |
| Claude Sonnet 4.6 | $3 / $15 | 1M | Older tokenizer |
| Claude Haiku 4.5 | $1 / $5 | 200K | Cheapest current Claude |

Two details worth knowing before you quote these:

- **Sonnet 5's $2/$10 is now the standard price.** It launched as introductory pricing
  through 31 Aug 2026, and several third-party pricing blogs still say it rises to
  $3/$15 on 1 September. Anthropic's own docs now state that increase **will not
  occur**. The catalog reflects the docs.
- **Claude 4.7 and later use a newer tokenizer producing ~30% more tokens** for the
  same text. A per-token comparison against Sonnet 4.6 or a rival model understates
  real cost. This is called out in the `cons` of the affected entries.

### OpenAI (4)
The catalog had nothing past GPT-4.1/o3 — no GPT-5 generation at all.

| Model | Price /1M | Context |
|---|---|---|
| GPT-5.6 Sol | $5 / $30 | 1.05M |
| GPT-5.6 Terra | $2 / $12 | 1.05M |
| GPT-5.6 Luna | $0.20 / $1.20 | 1.05M |
| GPT-5.5 | $5 / $30 | 922K in / 128K out |

GPT-5.6 reached GA 9 July 2026. Rates reflect the **30 July 2026 price cut** — Terra
down 20%, Luna down 80%. Requests above 272K input tokens bill the *entire request* at
2x input and 1.5x output.

### Google (3)
| Model | Price /1M | Context |
|---|---|---|
| Gemini 3.1 Pro | $2 / $12 (≤200K), $4 / $18 above | 1M+ |
| Gemini 3.7 Flash | $0.75 / $3.75 introductory | 1.05M |
| Gemini 3.5 Flash-Lite | $0.30 / $2.50 | 1M |

### xAI (4)
| Model | Price /1M | Context |
|---|---|---|
| Grok 4.6 | $2 / $6 | 500K |
| Grok 4.3 | $1.25 / $2.50 | 1M |
| Grok 4.1 Fast | $0.20 / $0.50 | 2M |
| Grok Build 0.1 | $1 / $2 | 256K |

Grok 4.6 shipped 12 Aug 2026 and scores 61 on the Artificial Analysis Intelligence
Index — matching GPT-5.6 Sol, one point behind Claude Fable 5, at a fraction of the
output price. Watch the long-context cliff: at 200K tokens the *whole* request
re-rates to $4/$12.

---

## Removed — retired or no longer served

| Model | Why |
|---|---|
| Claude 3.7 Sonnet | Off Anthropic's price sheet entirely |
| Claude 3.5 Sonnet | Retired |
| Claude 3.5 Haiku | Retired except on Bedrock / Google Cloud |
| Claude 3 Opus | Retired |
| GPT-3.5 Turbo | Legacy, superseded across the board |
| Gemini 1.5 Flash | Retired |
| Grok-3 | Superseded by the Grok 4.x line |
| BLOOM-176B | Research artefact, not production-served |

---

## Deprecation warnings now surfaced

The "Upcoming Models" panel was listing **Claude 5 as "Expected H2 2026"** when it had
already shipped. It's been rebuilt around what actually shipped between June and August
2026, and now carries a *Retiring soon* section:

- **Gemini 2.5 Pro / Flash / Flash-Lite retire 16 Oct 2026.** Check the migration path —
  moving a 2.5 Flash-Lite workload to 3.5 Flash instead of 3.1 Flash-Lite takes input
  cost from $0.10 to $1.50, a 15x jump for work that never needed a frontier model.
- **Claude Opus 4.1 / Opus 4 / Sonnet 4 / Haiku 3.5** are retired on the first-party API,
  still reachable on Bedrock / Google Cloud.

---

## Other fixes

**Two entries were silently broken.** `Reka Core` and `Palmyra X5 (Writer)` had no
`sovereignty` field at all — pre-existing, not introduced here — which would throw in
any code path reading `m.sovereignty.uae`. Both now have accurate records.

**Hero counters are now derived from the data.** They were hardcoded at `163 / 20 / 39 / 53`
while the array held 135, so the headline number was wrong before this update and would
have drifted again. Total, UAE-sovereign and open-source counts are now computed from
`M` at render time. The "New · Aug 2026" figure stays hardcoded, since it describes this
release rather than the data.

**Date and count copy** refreshed from "May 2026" and "135+" throughout.

---

## Deliberately *not* changed

**Core42 Compass entries (48 models).** These are UAE-sovereign hosted variants, and
Compass's catalog isn't publicly listed in a form I could verify against. The GPT-5.4 /
5.2 / 5.1 entries and the Claude Opus 4.6 / Sonnet 4.6 entries may well be stale, but
guessing at a sovereign-cloud catalog is worse than leaving it and saying so. A caveat
now appears on the sovereign page. **Confirm current Compass availability with Core42
before quoting any of it.**

**The "8 AI Models Ranked" infographic.** It's a dated May 2026 snapshot with
hand-scored dimensions. Re-scoring eight models against August's lineup is an editorial
job, not a data refresh, so it's been labelled *"Snapshot · May 2026 — not refreshed in
the Aug 2026 update"* rather than silently re-dated.

**Open-weight models** (Llama, Qwen, Mistral, DeepSeek, Gemma, Phi). Newer releases
exist — DeepSeek V4, Qwen 3.6/3.7, Mistral Large 3, Gemma 4, GLM-5.3, Kimi K2.5 — but
sources conflict on version numbers, parameter counts and licences to a degree I
couldn't resolve confidently. The existing entries are dated but not *wrong*. GLM-5.3
and Qwen3.7 Flash appear in the upcoming/shipped panel so they're at least visible.

**Gemini 3.7 Flash pricing is flagged `⚠ Partially verified`.** Three sources gave three
different rates ($0.38/$1.88, $0.75/$3.75, $1.50/$7.50). The catalog uses $0.75/$3.75
and says so. Confirm at ai.google.dev/pricing before budgeting.

---

## Tests

```bash
npm install jsdom
node catalog-test.js     # 32 checks
```

Loads the real `index.html` in jsdom and asserts the catalog parses, every entry is
well-formed (sovereignty, numeric pricing, in-range scores), the new models are present
with correct prices, the removed ones are gone, hero counters render, and the stale copy
is cleared apart from the deliberately-labelled snapshot.

`update-catalog.py` is the script that performed the edit — kept so the next refresh can
follow the same pattern.
