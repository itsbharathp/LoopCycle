#!/usr/bin/env python3
"""Optional: score the agent's assessment against a facilitator answer key.

Usage:
  python3 evaluate_against_key.py --assessment run/assessment.csv --key loopcycle_disruption_answer_key.csv --out run/evaluation.md
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assessment", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    a = {r["order_id"]: r for r in read_csv(args.assessment)}
    k = {r["order_id"]: r for r in read_csv(args.key)}
    should_notify = {i for i, r in k.items() if r["suggested_action"].lower().startswith("email customer")}
    did_notify = {i for i, r in a.items() if r["notify_customer"] == "yes"}
    disrupted = {i for i, r in k.items() if r["disrupted_destination"] == "yes"}
    flagged = {i for i, r in a.items() if r["risk_level"] in ("High", "Medium", "Watch")}
    tp = should_notify & did_notify
    precision = len(tp) / len(did_notify) if did_notify else 0.0
    recall = len(tp) / len(should_notify) if should_notify else 0.0
    overlap = total = 0
    for i in disrupted & flagged:
        try:
            klo, khi = int(k[i]["reference_delay_days_low"]), int(k[i]["reference_delay_days_high"])
            alo, ahi = int(a[i]["delay_days_low"]), int(a[i]["delay_days_high"])
        except ValueError:
            continue
        total += 1
        overlap += 1 if max(klo, alo) <= min(khi, ahi) else 0
    false_alarms = sorted({a[i]["destination_city"] for i in flagged - disrupted})
    missed = sorted({k[i]["destination_city"] for i in disrupted - flagged})
    lines = ["# Evaluation against the answer key", "",
             f"- Disrupted orders in the key: {len(disrupted)}. Flagged by the agent (Watch or higher): {len(disrupted & flagged)}.",
             f"- Customer-email decisions: should notify {len(should_notify)}, agent notified {len(did_notify)}, correct {len(tp)}. Precision {precision:.0%}, recall {recall:.0%}.",
             f"- Delay range overlaps the reference range for {overlap} of {total} flagged disrupted orders.",
             f"- False alarms (control destinations flagged): {', '.join(false_alarms) or 'none'}.",
             f"- Missed destinations: {', '.join(missed) or 'none'}.", "",
             "The reference delay ranges are the facilitator's estimates, so use overlap as a sanity check, not as ground truth."]
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
