#!/usr/bin/env python3
"""Phase 3: combine open orders with verified disruption findings.

Usage:
  python3 assess_orders.py --orders orders.csv --findings findings.json --out ./run \
      [--as-of 2026-10-13] [--min-notify Medium] [--holidays 2026-12-25] [--offer-cancellation] [--brand LoopCycle]

Writes in --out: assessment.csv, assessment.json, report.md, customer_emails.csv
"""
import argparse
import collections
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (OPEN_STATUSES, SEV_LABEL, SEV_RANK, add_business_days, dest_key, norm, parse_date, parse_holidays,
                    pick_destination_columns, read_csv, read_json, write_csv, write_json)

# Starting-point delay ranges (business days) used only when a finding gives no source-based numbers.
RUBRIC_DELAY = {"low": (0, 1), "medium": (1, 3), "high": (3, 6)}

ACTIONS = {
    ("high", "Ordered"): "Notify the customer now with the revised window. Hold dispatch or choose an alternative route or courier. Offer address change or wait.",
    ("high", "Packed"): "Notify the customer now. Hold or reroute via an alternative hub or courier and confirm the courier will accept the shipment. Re-check daily.",
    ("high", "In-Transit"): "Notify the customer now. Ask the courier for status and reroute or return options. Re-check daily.",
    ("medium", "Ordered"): "Notify the customer proactively with the revised window. Ship with the most resilient courier. Re-check in 24 hours.",
    ("medium", "Packed"): "Notify the customer proactively. Confirm courier capacity for the area before handover. Re-check in 24 hours.",
    ("medium", "In-Transit"): "Notify the customer. Watch tracking daily and contact the courier if there is no scan in 48 hours.",
    ("low", "Ordered"): "Monitor only. No customer email. Re-check at the next run.",
    ("low", "Packed"): "Monitor only. Email only if the shipment is held. Re-check at the next run.",
    ("low", "In-Transit"): "Monitor tracking. Email only if there is no scan in 48 hours.",
}

TYPE_LABELS = {"flood": "Flooding", "heavy_rain": "Heavy rain warning", "storm": "Storm", "volcano": "Volcanic activity", "fire_haze": "Fires and haze",
               "haze_air_quality": "Haze (air quality)", "high_waves": "High waves", "strike": "Strike", "protest": "Protest or unrest", "earthquake": "Earthquake",
               "closure": "Road or port closure", "other": "Disruption"}


def sev_of(finding):
    sev = norm(finding.get("severity")).lower() or "none"
    sev = sev if sev in SEV_RANK else "none"
    impact = norm(finding.get("affects_logistics")).lower()
    if impact == "no":
        sev = min(sev, "low", key=lambda s: SEV_RANK[s])
    elif impact == "unclear":
        sev = min(sev, "medium", key=lambda s: SEV_RANK[s])
    return sev


def delays_of(finding, sev):
    lo, hi = finding.get("delay_days_low"), finding.get("delay_days_high")
    if lo is None or hi is None:
        lo, hi = RUBRIC_DELAY.get(sev, (0, 0))
        return int(lo), int(hi), "rubric default (no source-based figure)"
    return int(lo), int(hi), "finding estimate"


def customer_email(order, a, brand, offer_cancel):
    first = norm(order.get("customer_first_name")) or "there"
    courier = norm(order.get("courier"))
    status = a["status"]
    if status == "In-Transit":
        doing = f"We are tracking your parcel{' with ' + courier if courier else ''} and will tell you if the estimate changes."
    elif status == "Packed":
        doing = "Your order is packed. We are choosing the most reliable route to you and will confirm once it ships."
    else:
        doing = "We will dispatch your order as soon as it is ready, using the most reliable route available."
    option = ("If you would rather cancel for a full refund, just reply and we will take care of it." if offer_cancel
              else "If you would like to change the delivery address or have any questions, just reply to this email.")
    subject = f"Update on your {brand} order {a['order_id']}: delivery may be delayed"
    body = (f"Hi {first},\n\nThank you for your order ({norm(order.get('product_name')) or 'your order'}, {a['order_id']}). "
            f"We are writing because we have seen a disruption that may delay delivery to {a['destination_city']}.\n\n"
            f"What is happening: {a['customer_reason']}\n"
            f"Original delivery date: {a['expected_delivery_date']}\n"
            f"Updated estimate: between {a['revised_eta_low']} and {a['revised_eta_high']}\n\n"
            f"What we are doing: {doing}\n\n{option}\n\nWe are sorry for the inconvenience and thank you for your patience.\n\nThe {brand} team")
    return subject, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", required=True)
    parser.add_argument("--findings", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--min-notify", default="Medium", choices=["Low", "Medium", "High"])
    parser.add_argument("--holidays", default="")
    parser.add_argument("--statuses", default=",".join(OPEN_STATUSES))
    parser.add_argument("--offer-cancellation", action="store_true")
    parser.add_argument("--brand", default="LoopCycle")
    args = parser.parse_args()

    as_of = parse_date(args.as_of)
    holidays = parse_holidays(args.holidays)
    statuses = {s.strip().lower() for s in args.statuses.split(",") if s.strip()}
    min_rank = SEV_RANK[args.min_notify.lower()]
    orders = [r for r in read_csv(args.orders) if norm(r["status"]).lower() in statuses]
    c_city, c_prov, c_country, _, _ = pick_destination_columns(orders[0].keys())
    data = read_json(args.findings)
    findings = data.get("findings", [])
    checked = {c["key"]: c for c in data.get("destinations_checked", [])}

    by_dest = collections.defaultdict(list)
    for f in findings:
        for key in f.get("affected_destinations", []):
            by_dest[key].append(f)

    results = []
    for o in orders:
        key = dest_key(o[c_city], o[c_country])
        fs = [(f, sev_of(f)) for f in by_dest.get(key, [])]
        fs = [(f, s) for f, s in fs if s != "none"]
        expected = parse_date(o["expected_delivery_date"])
        base = {"order_id": o["order_id"], "platform": norm(o.get("platform")), "status": norm(o["status"]), "destination_city": norm(o[c_city]),
                "destination_country": norm(o[c_country]).upper(), "expected_delivery_date": expected.isoformat(), "days_until_delivery": (expected - as_of).days,
                "courier": norm(o.get("courier")), "customer_email": norm(o.get("customer_email")), "email_opt_in": norm(o.get("email_opt_in")) or "unknown"}
        if not fs:
            risk = "On track" if key in checked else "Not checked"
            base.update({"risk_level": risk, "severity": "none", "delay_days_low": 0, "delay_days_high": 0, "revised_eta_low": expected.isoformat(), "revised_eta_high": expected.isoformat(),
                         "reason": "No active disruption found for this destination at the time of the search." if risk == "On track" else "Destination was not searched. Run the search for this destination.",
                         "customer_reason": "", "disruption_ids": "", "disruption_types": "", "confidence": "", "delay_basis": "", "sources": "",
                         "suggested_action": "No action." if risk == "On track" else "Search this destination before shipping.", "notify_customer": "no", "email_block_reason": ""})
            results.append(base)
            continue
        fs.sort(key=lambda x: (SEV_RANK[x[1]], delays_of(x[0], x[1])[1]), reverse=True)
        gov, sev = fs[0]
        lo, hi, basis = delays_of(gov, sev)
        eta_lo, eta_hi = add_business_days(expected, lo, holidays), add_business_days(expected, hi, holidays)
        reasons = "; ".join(dict.fromkeys(f"{TYPE_LABELS.get(f.get('type'), 'Disruption')}: {norm(f.get('summary'))}" for f, _ in fs))
        urls = []
        for f, _ in fs:
            for s in f.get("sources", []):
                if s.get("url") and s["url"] not in urls:
                    urls.append(s["url"])
        notify = SEV_RANK[sev] >= min_rank
        block = ""
        if notify:
            email = norm(o.get("customer_email"))
            if not email:
                block = "no email on file"
            elif norm(o.get("email_opt_in")).lower() == "no":
                block = "customer opted out of email"
            elif email.lower().rsplit("@", 1)[-1] in ("example.com", "example.org", "example.net"):
                block = "demo address (example domain), do not send"
        base.update({"risk_level": SEV_LABEL[SEV_RANK[sev]], "severity": sev, "delay_days_low": lo, "delay_days_high": hi, "revised_eta_low": eta_lo.isoformat(), "revised_eta_high": eta_hi.isoformat(),
                     "reason": reasons, "customer_reason": norm(gov.get("customer_message")) or f"{TYPE_LABELS.get(gov.get('type'), 'A disruption')} is affecting {norm(o[c_city])}.",
                     "disruption_ids": ",".join(dict.fromkeys(f.get("id", "") for f, _ in fs)), "disruption_types": ",".join(dict.fromkeys(norm(f.get("type")) for f, _ in fs)),
                     "confidence": norm(gov.get("confidence")), "delay_basis": basis, "sources": " | ".join(urls),
                     "suggested_action": ACTIONS[(sev, base["status"])] if (sev, base["status"]) in ACTIONS else "Review manually.",
                     "notify_customer": "yes" if notify else "no", "email_block_reason": block})
        results.append(base)

    os.makedirs(args.out, exist_ok=True)
    fields = ["order_id", "platform", "status", "destination_city", "destination_country", "risk_level", "severity", "expected_delivery_date", "delay_days_low", "delay_days_high",
              "revised_eta_low", "revised_eta_high", "reason", "suggested_action", "notify_customer", "email_block_reason", "disruption_ids", "disruption_types", "confidence",
              "delay_basis", "sources", "days_until_delivery", "courier", "customer_email", "email_opt_in", "customer_reason"]
    order_rank = {"High": 0, "Medium": 1, "Watch": 2, "Not checked": 3, "On track": 4}
    results.sort(key=lambda r: (order_rank[r["risk_level"]], r["days_until_delivery"], r["order_id"]))
    write_csv(os.path.join(args.out, "assessment.csv"), results, fields)
    write_json(os.path.join(args.out, "assessment.json"), results)

    # customer email drafts
    by_id = {o["order_id"]: o for o in orders}
    drafts = []
    for a in results:
        if a["notify_customer"] == "yes":
            subject, body = customer_email(by_id[a["order_id"]], a, args.brand, args.offer_cancellation)
            drafts.append({"order_id": a["order_id"], "to": a["customer_email"], "send_allowed": "no" if a["email_block_reason"] else "yes", "block_reason": a["email_block_reason"], "subject": subject, "body": body})
    write_csv(os.path.join(args.out, "customer_emails.csv"), drafts, ["order_id", "to", "send_allowed", "block_reason", "subject", "body"])

    # report
    counts = collections.Counter(r["risk_level"] for r in results)
    at_risk = [r for r in results if r["risk_level"] in ("High", "Medium", "Watch")]
    lines = [f"# Delivery disruption update ({as_of.isoformat()})", "",
             f"**Open orders checked:** {len(results)}. **At risk:** {counts['High'] + counts['Medium']} (High {counts['High']}, Medium {counts['Medium']}). **Watch:** {counts['Watch']}. **On track:** {counts['On track']}. **Not checked:** {counts['Not checked']}.",
             f"**Customer emails:** {len(drafts)} drafted, {sum(1 for d in drafts if d['send_allowed'] == 'yes')} allowed to send, {sum(1 for d in drafts if d['send_allowed'] == 'no')} blocked (opt-out, no address or demo address). Nothing is sent without approval.", ""]
    groups = collections.OrderedDict()
    for r in at_risk:
        groups.setdefault((r["destination_city"], r["destination_country"], r["disruption_ids"]), []).append(r)
    if groups:
        lines += ["## Destinations needing attention", "", "| Destination | Orders | Status mix | Risk | Delay (business days) | Revised delivery window | Reason | Suggested action |", "|---|---|---|---|---|---|---|---|"]
        for (city, country, _), rs in groups.items():
            sm = collections.Counter(x["status"] for x in rs)
            r0 = rs[0]
            window = f"{min(x['revised_eta_low'] for x in rs)} to {max(x['revised_eta_high'] for x in rs)}"
            lines.append(f"| {city}, {country} | {len(rs)} | {', '.join(f'{k} {v}' for k, v in sm.items())} | {r0['risk_level']} | {r0['delay_days_low']} to {r0['delay_days_high']} | {window} | {r0['reason']} | {r0['suggested_action']} |")
        lines += ["", "## Order-level detail", "", "| Order | Status | Destination | Original delivery | Revised window | Risk | Notify customer |", "|---|---|---|---|---|---|---|"]
        for r in at_risk:
            note = r["notify_customer"] + (f" ({r['email_block_reason']})" if r["email_block_reason"] else "")
            lines.append(f"| {r['order_id']} | {r['status']} | {r['destination_city']} | {r['expected_delivery_date']} | {r['revised_eta_low']} to {r['revised_eta_high']} | {r['risk_level']} | {note} |")
        lines += ["", "## Sources", ""]
        seen = set()
        for f in findings:
            for s in f.get("sources", []):
                if s.get("url") and s["url"] not in seen:
                    seen.add(s["url"])
                    lines.append(f"- {norm(f.get('id'))}: [{norm(s.get('title')) or s['url']}]({s['url']}) ({norm(s.get('publisher'))}, {norm(s.get('published'))})")
    else:
        lines += ["No open orders are currently at risk."]
    unchecked = [r for r in results if r["risk_level"] == "Not checked"]
    if unchecked:
        lines += ["", f"## Not checked ({len(unchecked)} orders)", "", "These destinations were not searched: " + ", ".join(sorted({r['destination_city'] for r in unchecked}))]
    lines += ["", "## How to read this", "",
              "- Delay figures are estimates in business days. Where the source gave no figure, a starting-point range from the rubric was used (see the `delay_basis` column in assessment.csv).",
              "- Revised windows add the delay range to the original delivery date, skipping weekends and any holidays supplied.",
              "- Conditions change quickly. Re-run before contacting customers, and have a person approve any customer emails."]
    with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"assessed {len(results)} orders: {dict(counts)}; {len(drafts)} email drafts -> {args.out}")


if __name__ == "__main__":
    main()
