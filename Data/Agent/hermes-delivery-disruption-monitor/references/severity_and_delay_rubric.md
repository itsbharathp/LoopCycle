# Severity and delay rubric

These are starting points. Calibrate them against your couriers' real delay history.

## Severity

| Severity | Meaning | Typical evidence |
|---|---|---|
| High | Likely to delay parcels materially or stop movement for several days | Official closures, flooded or cut roads, airport or port closure, nationwide postal or transport strike with confirmed service suspension |
| Medium | Likely to slow parcels by a day or more | Official weather or hazard warnings for the destination, flight cancellations at a nearby airport, regional strike with notices from the postal operator or courier, sea crossings restricted |
| Low | Hazard exists but no sign of parcel impact yet | Air-quality alerts, volcano alert raised without closures, long-running strike that carriers already work around |
| None | Nothing found | No relevant, active, sourced event |

Caps applied by the script: `affects_logistics: no` caps severity at Low, `unclear` caps it at Medium.

## Delay ranges in business days (starting points)

| Type | Low | Medium | High |
|---|---|---|---|
| flood, heavy_rain, storm | 0 to 1 | 1 to 3 | 3 to 6 |
| volcano | 0 to 2 | 2 to 4 | 4 to 7 |
| fire_haze | 0 to 2 | 1 to 3 | 3 to 5 |
| haze_air_quality | 0 to 1 | 1 to 2 | n/a |
| high_waves (sea crossing) | 0 to 1 | 1 to 3 | 3 to 5 |
| strike (postal, port, airport) | 0 to 2 | 1 to 3 | 3 to 7 |
| protest, unrest | 0 to 1 | 1 to 3 | 3 to 5 |
| earthquake | 0 to 2 | 2 to 4 | 4 to 8 |

If a source states a delay, closure period or restoration date, use it and say so in `delay_basis`.

## Adjustments

- Add 1 business day to the high end when the event is forecast to continue past the order's original delivery date.
- International shipments: add 1 day to the high end if the disruption affects a hub airport or customs.
- Parcels already In-Transit may be past the affected stretch. Prefer the lower end if tracking shows the parcel has already cleared the area (only if you have tracking data).
- Holidays: pass destination holidays with `--holidays` so revised windows skip them.

## Action table (implemented in `assess_orders.py`)

| Severity | Ordered | Packed | In-Transit |
|---|---|---|---|
| High | Notify now, hold or reroute, offer address change | Notify now, hold or reroute, confirm courier acceptance | Notify now, contact courier for reroute or return options |
| Medium | Notify with revised window, use the most resilient courier | Notify, confirm courier capacity | Notify, watch tracking, contact courier after 48 hours without a scan |
| Low | Monitor | Monitor, email if held | Monitor, email if no scan in 48 hours |
