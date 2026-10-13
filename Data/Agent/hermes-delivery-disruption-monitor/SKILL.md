---
name: hermes-delivery-disruption-monitor
description: >
  Monitors open customer orders (Ordered, Packed, In-Transit) for delivery delays
  caused by active disruptions at the destination: floods, storms, volcanic
  eruptions, fires and haze, strikes, protests, unrest, closures and similar.
  Reads the order file, searches the web for current disruptions at each
  destination, verifies the sources, predicts the delay, and reports the revised
  delivery window, the reason and a suggested action for each affected order. It
  also drafts customer emails for approval. Triggers whenever the user says
  "check delivery disruptions", "which orders are at risk", "delay update",
  "any delays on open orders", "run the disruption monitor", "update me on
  delivery delays", or asks whether weather, strikes, protests or disasters will
  delay orders. Also triggers on a schedule. Always use this skill for any task
  that combines order data with disruption or delay checks. Do not improvise ad
  hoc searches.

metadata:
  hermes:
    triggers:
      - type: schedule
        interval_minutes: 360
        on_trigger: run_workflow
      - type: user_phrase
        patterns:
          - "check delivery disruptions"
          - "which orders are at risk"
          - "delay update"
          - "any delays on open orders"
          - "run the disruption monitor"
          - "will my orders be delayed"
    config:
      - key: orders_path
        description: "Path to the open orders CSV (see references/order_schema.md)."
        prompt: "Where is the open orders CSV?"
        default: "~/orders/open_orders.csv"
      - key: output_dir
        description: "Directory where each run writes its files."
        prompt: "Where should run outputs be saved?"
        default: "~/disruption-monitor/runs"
      - key: statuses_in_scope
        description: "Order statuses to monitor."
        default: "Ordered,Packed,In-Transit"
      - key: min_notify_severity
        description: "Lowest severity (Low, Medium, High) that triggers a customer email draft."
        default: "Medium"
      - key: search_lookback_days
        description: "How recent a source must be for an event to count as active."
        default: "7"
      - key: send_customer_emails
        description: "If false, customer emails are drafted only. If true, they are sent after the operator approves."
        prompt: "Should customer emails be sent after approval (true) or only drafted (false)?"
        default: "false"
      - key: offer_cancellation
        description: "If true, drafts offer a cancellation with full refund. Leave false unless the business has approved this."
        default: "false"
      - key: operator_email
        description: "Where to send the update summary (optional)."
        default: ""
      - key: brand_name
        description: "Brand name used in customer emails."
        default: "LoopCycle"
      - key: holidays
        description: "Comma-separated ISO dates to skip when calculating revised windows."
        default: ""
      - key: sent_log_path
        description: "File that records customer emails already sent, to prevent duplicates."
        default: "~/disruption-monitor/sent_log.json"
---

# Hermes Delivery Disruption Monitor

This skill answers one question for the operator: **which open orders will be late, why, by how much, and what should we do?**

It reads open orders, researches active disruptions at each destination on the live web, checks the sources, estimates the delay, and produces an update plus customer email drafts. A person approves anything that goes to a customer.

Read `references/search_playbook.md` before Phase 2, `references/severity_and_delay_rubric.md` before assigning severity, `references/findings_schema.md` for the findings file, and `references/email_templates.md` for customer wording. Order columns are in `references/order_schema.md`.

---

## Trigger Conditions

This workflow runs when **any** of the following is true:

1. Hermes's scheduler fires every `interval_minutes` (default 360).
2. The user asks for a disruption or delay update (see the trigger phrases above).
3. The user asks about a specific order or destination (for example "will order #LT10916 be late?"). In that case run the workflow for that order or destination only.

---

## Step-by-Step Workflow

### PHASE 1: Load open orders

Run:

```bash
python3 scripts/load_orders.py --orders {{orders_path}} --out {{output_dir}}/<YYYY-MM-DD_HHMM> --statuses "{{statuses_in_scope}}" --as-of <today>
```

This writes `orders_in_scope.csv`, `destinations.json` (destinations, order counts, search groups with ready-made queries and source hints) and `search_plan.md`.

- If the file is missing, empty or lacks the required columns, **stop** and tell the user exactly what is missing. Do not guess columns.
- If there are no open orders, say so and stop (stay silent on a scheduled run).

### PHASE 2: Search for active disruptions

Follow `references/search_playbook.md`. For each search group in `destinations.json`:

1. Run the queries for the group, adding more only if needed. Prefer official sources (weather, disaster and volcano agencies, airport and postal notices, courier notices).
2. **Open the sources.** Do not rely on snippets.
3. Apply the four tests: active, located, logistics-relevant, sourced.
4. Record each real event once in `findings.json` (see `findings_schema.md`), listing every affected destination key.
5. Record every destination you searched in `destinations_checked`, with `disruption_found` or `no_disruption_found`.

Rules:

- **Never invent** events, numbers, alert levels or URLs. If nothing is found, record `no_disruption_found` and say "none found", not "safe".
- Label every delay estimate as an estimate in `delay_basis`.
- Use the more cautious severity when sources conflict.
- If a High severity finding rests on one non-official source, mark it `confidence: low` and `verified: false`, and flag it to the user.

### PHASE 3: Assess every open order

Run:

```bash
python3 scripts/assess_orders.py --orders {{orders_path}} --findings <run_dir>/findings.json --out <run_dir> --as-of <today> --min-notify {{min_notify_severity}} --holidays "{{holidays}}" --brand "{{brand_name}}"
```

(Add `--offer-cancellation` only if the config says so.) It writes `assessment.csv`, `assessment.json`, `report.md` and `customer_emails.csv`.

Check the output before reporting:

- Every destination should be `On track`, `Watch`, `Medium` or `High`. Any `Not checked` means Phase 2 missed a destination. Go back and search it.
- Sanity-check delay ranges against the rubric and the sources. Adjust `findings.json` and re-run if they look wrong.

### PHASE 4: Give the operator an update

Use this format in chat. Keep it to one screen and point to `report.md` for the rest.

```
Delivery disruption update, <date>

Open orders checked: <N>. At risk: <N> (High <n>, Medium <n>). Watch: <n>. On track: <n>.

Destination | Orders | Delay | Original -> revised delivery | Reason | Suggested action
...

Customer emails drafted: <n> (<n> blocked: opt-out, no address or demo address).
Not verified / low confidence: <list or "none">
Sources: <links>
```

If the run was scheduled and nothing is at risk, stay silent. If a High finding is new or has worsened since the last run, lead with it.

### PHASE 5: Customer emails (approval required)

Default is **draft only**. Do not send anything unless `send_customer_emails` is true **and** the operator approves in this conversation.

1. Show the count and a sample draft. Ask: "Send these N emails? (yes / no / send High only)".
2. Send only rows in `customer_emails.csv` with `send_allowed = yes`. Never override a block (opt-out, no address, demo address).
3. Check `sent_log_path` first. Send at most one email per order per disruption, unless the revised window moves by 2 or more business days.
4. After sending, append `order_id`, `disruption_ids`, `sent_at` and the revised window to `sent_log_path`.
5. Do not offer refunds, cancellation or compensation in the email unless `offer_cancellation` is true.

### PHASE 6: Log and re-check

- Save `run_log.json` (time, orders checked, findings, emails sent, anything unverified).
- Compare with the previous run: report **new**, **worsened** and **resolved** events. For resolved events with emails already sent, offer an all-clear message (needs approval).
- Re-run daily for any destination at High risk until it clears.

---

## Where AI helps and where a person decides

| The agent does | The agent drafts, a person approves | A person decides |
|---|---|---|
| Reads orders, builds the search plan, searches, collects sources, estimates delay ranges, calculates revised windows, drafts emails | Customer emails, all-clear messages, courier reroute requests | What to promise customers, refunds, cancellations and compensation, paying for faster routes, whether to stop shipping to an area, anything touching safety |

---

## Error Handling & Guardrails

| Scenario | Action |
|---|---|
| Orders file missing or malformed | Stop, say what is missing |
| Web search unavailable | Say so. Do not fall back on memory. Report orders as Not checked |
| A source cannot be opened | `verified: false`, `confidence: low`, say so in the update |
| Sources conflict | Record both, use the more cautious severity |
| Destination not searched | Report as Not checked, never as on track |
| Customer opted out or no email | Block the draft and tell the operator |
| Demo address (example.com, example.org) | Block the draft |
| Evidence of danger to people near a destination | Stop and ask the operator before doing anything else |

**Hard rules:**

- **Never invent** a disruption, source, URL, statistic or alert level.
- **Never send** a customer email without operator approval in this conversation.
- **Never promise** a delivery date. Give a window and say it may change.
- **Never email** a customer who opted out.
- **Always cite** sources you actually opened, with publisher and date.

---

## Tool Requirements (Hermes MCP Connectors)

| Connector | Used for |
|---|---|
| Web search and page fetch | Finding and reading disruption sources (required) |
| Filesystem | Reading orders, writing run files and logs |
| Python 3 (standard library only) | Running `scripts/` |
| Gmail (optional) | Sending approved customer emails and the operator summary |

If web search is not connected, tell the user: "Connect a web search tool before I can check for disruptions."

---

## File Layout

```
hermes-delivery-disruption-monitor/
├── SKILL.md                         ← you are here
├── README.md                        ← install, test and customise
├── references/
│   ├── search_playbook.md           ← how to query, verify and avoid made-up facts
│   ├── severity_and_delay_rubric.md ← severity levels, delay ranges, action table
│   ├── findings_schema.md           ← format of findings.json
│   ├── order_schema.md              ← order columns
│   └── email_templates.md           ← customer and operator wording
├── scripts/
│   ├── common.py                    ← business-day and file helpers
│   ├── load_orders.py               ← Phase 1: orders to search plan
│   ├── assess_orders.py             ← Phase 3: orders + findings to report and drafts
│   └── evaluate_against_key.py      ← optional scoring against a facilitator key
└── examples/
    ├── demo_orders.csv              ← 100 sample open orders
    ├── demo_answer_key.csv          ← facilitator answer key (do not show the agent)
    ├── sample_findings.json         ← pre-filled findings for an offline dry run
    └── sample_output/               ← output of the dry run
```
