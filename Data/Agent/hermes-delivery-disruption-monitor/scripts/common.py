"""Shared helpers for the delivery disruption monitor (standard library only)."""
import csv
import json
from datetime import date, datetime, timedelta

SEV_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3}
SEV_LABEL = {0: "On track", 1: "Watch", 2: "Medium", 3: "High"}
OPEN_STATUSES = ["Ordered", "Packed", "In-Transit"]

COUNTRY_NAMES = {
    "ID": "Indonesia", "SG": "Singapore", "MY": "Malaysia", "BE": "Belgium", "ES": "Spain",
    "AU": "Australia", "JP": "Japan", "US": "United States", "GB": "United Kingdom",
    "NL": "Netherlands", "DE": "Germany", "CA": "Canada", "FR": "France", "TH": "Thailand",
    "PH": "Philippines", "VN": "Vietnam", "IN": "India", "IT": "Italy", "MX": "Mexico",
}


def norm(value):
    return (value or "").strip()


def dest_key(city, country):
    """Stable destination key used to link orders and findings, e.g. 'Medan|ID'."""
    return f"{norm(city)}|{norm(country).upper()}"


def parse_date(value):
    value = norm(value)
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date: {value!r}")


def parse_holidays(text):
    out = set()
    for part in (text or "").split(","):
        part = part.strip()
        if part:
            out.add(parse_date(part))
    return out


def add_business_days(start, n, holidays=frozenset()):
    """Add n business days (Mon-Fri, skipping listed holidays) to a date."""
    current = start
    remaining = int(n)
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in holidays:
            remaining -= 1
    return current


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def pick_destination_columns(columns):
    """Return (city, province, country, lat, lon) column names present in the orders file."""
    options = [
        ("destination_city", "destination_province_state", "destination_country", "destination_latitude", "destination_longitude"),
        ("customer_city", "customer_province_state", "customer_country", None, None),
    ]
    for opt in options:
        if opt[0] in columns and opt[2] in columns:
            return opt
    raise SystemExit("Orders file needs destination_city + destination_country (or customer_city + customer_country).")
