#!/usr/bin/env python3
"""Phase 1: read open orders and build a destination-level search plan.

Usage:
  python3 load_orders.py --orders orders.csv --out ./run [--statuses "Ordered,Packed,In-Transit"] [--as-of 2026-10-13]

Writes in --out:
  orders_in_scope.csv   open orders only
  destinations.json     destinations, order counts and the search groups to research
  search_plan.md        the same plan in readable form
"""
import argparse
import collections
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (COUNTRY_NAMES, OPEN_STATUSES, dest_key, norm, parse_date, pick_destination_columns,
                    read_csv, write_csv, write_json)

SOURCE_HINTS = {
    "ID": ["BMKG (weather and sea conditions)", "BNPB (disasters)", "PVMBG / MAGMA Indonesia (volcanoes)", "Kemenhub and airport notices", "courier service notices (JNE, J&T, SiCepat, AnterAja)"],
    "SG": ["NEA (air quality, PSI)", "Changi Airport and Singapore Post notices"],
    "MY": ["MetMalaysia", "Department of Environment (API)", "Pos Malaysia notices"],
    "BE": ["bpost service notices", "Brussels Airport advisories", "national unions' strike calendars via credible news"],
    "ES": ["AENA airport notices", "Correos notices", "strike trackers backed by news reports"],
    "AU": ["Bureau of Meteorology warnings", "Australia Post service alerts"],
    "JP": ["Japan Meteorological Agency", "Japan Post service notices"],
    "US": ["National Weather Service / NHC", "USPS service alerts"],
    "GB": ["Met Office warnings", "Royal Mail service updates"],
}


def month_year(as_of: date) -> str:
    return as_of.strftime("%B %Y")


def build_queries(place, iso, province, cities, couriers, as_of):
    country = COUNTRY_NAMES.get(iso, iso)
    my = month_year(as_of)
    queries = [
        {"purpose": "natural hazards", "query": f"{place} {country} flood OR storm OR landslide OR earthquake OR volcano warning {my}"},
        {"purpose": "strikes and unrest", "query": f"{place} {country} strike OR protest OR unrest OR road closure {my}"},
        {"purpose": "air quality and fires", "query": f"{place} {country} haze OR wildfire OR air quality alert {my}"},
        {"purpose": "national logistics", "query": f"{country} postal OR courier OR airport OR port strike OR delay {my}"},
    ]
    if iso == "ID":
        queries += [
            {"purpose": "official weather (Indonesian)", "query": f"BMKG peringatan dini {province or place} hari ini"},
            {"purpose": "local disasters (Indonesian)", "query": f"banjir OR longsor OR erupsi OR kebakaran hutan {place} hari ini"},
        ]
    for courier in couriers[:2]:
        queries.append({"purpose": "courier notices", "query": f"{courier} delivery delay {place} {my}"})
    return queries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--statuses", default=",".join(OPEN_STATUSES))
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()

    as_of = parse_date(args.as_of)
    statuses = {s.strip().lower() for s in args.statuses.split(",") if s.strip()}
    rows = read_csv(args.orders)
    if not rows:
        raise SystemExit("Orders file is empty.")
    columns = rows[0].keys()
    missing = [c for c in ("order_id", "status", "expected_delivery_date") if c not in columns]
    if missing:
        raise SystemExit(f"Orders file is missing required columns: {missing}")
    c_city, c_prov, c_country, c_lat, c_lon = pick_destination_columns(columns)

    in_scope = [r for r in rows if norm(r["status"]).lower() in statuses]
    os.makedirs(args.out, exist_ok=True)
    write_csv(os.path.join(args.out, "orders_in_scope.csv"), in_scope, list(columns))

    by_dest = collections.OrderedDict()
    for r in in_scope:
        key = dest_key(r[c_city], r[c_country])
        d = by_dest.setdefault(key, {"key": key, "city": norm(r[c_city]), "province_state": norm(r.get(c_prov)), "country": norm(r[c_country]).upper(),
                                     "latitude": norm(r.get(c_lat)) if c_lat else "", "longitude": norm(r.get(c_lon)) if c_lon else "",
                                     "orders": 0, "status_counts": collections.Counter(), "order_ids": [], "couriers": set(), "platforms": set(), "expected": []})
        d["orders"] += 1
        d["status_counts"][norm(r["status"])] += 1
        d["order_ids"].append(r["order_id"])
        if norm(r.get("courier")):
            d["couriers"].add(norm(r["courier"]))
        if norm(r.get("platform")):
            d["platforms"].add(norm(r["platform"]))
        d["expected"].append(parse_date(r["expected_delivery_date"]))

    destinations = []
    for d in by_dest.values():
        destinations.append({**{k: v for k, v in d.items() if k not in ("status_counts", "couriers", "platforms", "expected")},
                             "status_counts": dict(d["status_counts"]), "couriers": sorted(d["couriers"]), "platforms": sorted(d["platforms"]),
                             "earliest_expected_delivery": min(d["expected"]).isoformat(), "latest_expected_delivery": max(d["expected"]).isoformat()})

    # Search groups: one group per province/state (or per city when no province) to keep the number of searches manageable.
    groups = collections.OrderedDict()
    for d in destinations:
        gkey = f"{d['province_state'] or d['city']}|{d['country']}"
        g = groups.setdefault(gkey, {"group": d["province_state"] or d["city"], "country": d["country"], "destinations": [], "orders": 0, "couriers": set()})
        g["destinations"].append(d["key"])
        g["orders"] += d["orders"]
        g["couriers"].update(d["couriers"])
    search_groups = []
    for g in groups.values():
        cities = [k.split("|")[0] for k in g["destinations"]]
        province = g["group"] if g["group"] not in cities else ""
        place = g["group"] if len(cities) > 1 or province else cities[0]
        search_groups.append({"group": g["group"], "country": g["country"], "destination_keys": g["destinations"], "orders": g["orders"],
                              "queries": build_queries(place, g["country"], province, cities, sorted(g["couriers"]), as_of),
                              "source_hints": SOURCE_HINTS.get(g["country"], ["national weather service", "national postal operator", "airport and port authority notices"])})

    plan = {"as_of": as_of.isoformat(), "orders_total": len(rows), "orders_in_scope": len(in_scope), "statuses_in_scope": sorted(statuses),
            "destinations": destinations, "search_groups": search_groups}
    write_json(os.path.join(args.out, "destinations.json"), plan)

    lines = [f"# Search plan ({as_of.isoformat()})", "", f"Orders in scope: {len(in_scope)} of {len(rows)}. Destinations: {len(destinations)}. Search groups: {len(search_groups)}.", ""]
    for g in search_groups:
        lines += [f"## {g['group']} ({g['country']}), {g['orders']} orders", "", "Destinations: " + ", ".join(k.split("|")[0] for k in g["destination_keys"]), "",
                  "Prefer these sources: " + "; ".join(g["source_hints"]), "", "Queries:"]
        lines += [f"- ({q['purpose']}) {q['query']}" for q in g["queries"]] + [""]
    with open(os.path.join(args.out, "search_plan.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print(f"{len(in_scope)} open orders, {len(destinations)} destinations, {len(search_groups)} search groups -> {args.out}")


if __name__ == "__main__":
    main()
