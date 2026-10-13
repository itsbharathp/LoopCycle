# Hermes Delivery Disruption Monitor

A Hermes skill that reads open orders, searches the web for active disruptions at each destination, and tells you which orders will be late, by how much, why, and what to do. It also drafts customer emails for your approval.

## What you get from each run

- **An update** in chat: orders at risk, revised delivery windows, reasons, suggested actions, sources.
- `assessment.csv` / `assessment.json`: one row per open order.
- `report.md`: the update as a document.
- `customer_emails.csv`: email drafts (nothing is sent without approval).

## How it works

```
orders.csv -> load_orders.py -> search plan -> [Hermes agent searches the web, verifies sources] -> findings.json
                                                                                                      |
orders.csv + findings.json -> assess_orders.py -> assessment, report, email drafts -> you approve -> send
```

The agent does the searching and judging of sources. The scripts do the repeatable parts (reading orders, grouping destinations, business-day maths, report and drafts), so those results are consistent and testable.

## Install

1. Copy the `hermes-delivery-disruption-monitor/` folder into the directory where your Hermes install keeps its skills (next to your other `SKILL.md` folders).
2. Connect a **web search and page fetch** tool in Hermes. This is required. Connect Gmail only if you want to send emails.
3. Set the config values (the skill prompts for them): `orders_path` and `output_dir` at minimum.
4. Scheduling: the skill declares a schedule trigger (every 360 minutes) in the same style as your other Hermes skills. If you prefer `hermes cron`, register the skill with your Hermes CLI (check `hermes cron --help` for the syntax in your version).

Python 3 is required. The scripts use only the standard library.

## Try it with the demo data (no web search needed)

```bash
cd hermes-delivery-disruption-monitor
python3 scripts/load_orders.py --orders examples/demo_orders.csv --out run --as-of 2026-10-13
python3 scripts/assess_orders.py --orders examples/demo_orders.csv --findings examples/sample_findings.json --out run --as-of 2026-10-13
python3 scripts/evaluate_against_key.py --assessment run/assessment.csv --key examples/demo_answer_key.csv --out run/evaluation.md
```

`examples/sample_findings.json` is pre-filled from real news found on 12 and 13 October 2026, so this run only tests the pipeline. Open `examples/sample_output/report.md` to see the result.

## Run it for real (live web search)

In Hermes, say: **"check delivery disruptions"**. The agent will load the orders, search each destination group, write `findings.json`, run the assessment and give you the update. Then ask it to "send the drafts" if you want customers emailed.

To test the agent properly, give it `examples/demo_orders.csv` but **not** the answer key, then score it:

```bash
python3 scripts/evaluate_against_key.py --assessment <run_dir>/assessment.csv --key examples/demo_answer_key.csv --out <run_dir>/evaluation.md
```

The demo orders include 31 orders to destinations with real disruptions as of 13 October 2026 and 69 control orders. Conditions change, so a live run may legitimately differ from the key.

## Safety defaults

- Customer emails are **drafts only**. Sending needs `send_customer_emails: true` and your approval in the conversation.
- Customers who opted out, orders with no address and demo addresses (example.com, example.org) are blocked.
- The agent must open and cite its sources, and must say "none found" instead of "safe" when it finds nothing.
- Drafts never offer refunds or cancellation unless you set `offer_cancellation`.
- Delay figures are estimates and are labelled as such. Delay ranges that come from the rubric rather than a source are flagged in the `delay_basis` column.

## Customise

- **Severity and delay ranges:** edit `references/severity_and_delay_rubric.md` (and the `RUBRIC_DELAY` and `ACTIONS` tables in `scripts/assess_orders.py`).
- **Customer wording:** edit `customer_email()` in `scripts/assess_orders.py` and `references/email_templates.md`.
- **Who gets an email:** set `min_notify_severity` (Low, Medium or High).
- **Holidays:** pass `holidays` so revised windows skip them.
- **Countries and sources:** add official sources for new countries in `SOURCE_HINTS` in `scripts/load_orders.py`.

## Limits

- Search quality depends on the web search tool you connect. Local-language searches help for Indonesia.
- Delay predictions are heuristics, not courier data. Feed in courier tracking and historic delay data to improve them.
- The skill does not read live courier tracking by itself. Add a tracking connector if you want scan-based checks.
- The sample findings are a snapshot from 13 October 2026 and will go stale.
