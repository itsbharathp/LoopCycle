# findings.json schema

The agent writes this file at the end of Phase 2. `scripts/assess_orders.py` reads it.

```json
{
  "as_of": "2026-10-13",
  "findings": [
    {
      "id": "D01",
      "type": "flood",
      "severity": "high",
      "affects_logistics": "yes",
      "delay_days_low": 3,
      "delay_days_high": 6,
      "delay_basis": "estimate from event type and severity; not stated by the source",
      "summary": "Floods inundated 18 villages after heavy rain and embankment collapses; BMKG forecasts more rain.",
      "customer_message": "Heavy rain has caused flooding in the Aceh Tamiang area and some roads are affected.",
      "confidence": "high",
      "verified": true,
      "observed_at": "2026-10-13",
      "affected_destinations": ["Kuala Simpang|ID"],
      "sources": [
        {"title": "Floods Hit 18 Villages in Aceh as BMKG Warns of More Heavy Rain", "url": "https://...", "publisher": "Tempo", "published": "2026-10-12"}
      ]
    }
  ],
  "destinations_checked": [
    {"key": "Kuala Simpang|ID", "result": "disruption_found", "queries_tried": 6},
    {"key": "Jakarta|ID", "result": "no_disruption_found", "queries_tried": 6}
  ]
}
```

## Field rules

| Field | Rules |
|---|---|
| `id` | Short unique id for the event (one event can cover several destinations). |
| `type` | One of `flood`, `heavy_rain`, `storm`, `volcano`, `fire_haze`, `haze_air_quality`, `high_waves`, `strike`, `protest`, `earthquake`, `closure`, `other`. |
| `severity` | `none`, `low`, `medium` or `high`. See `severity_and_delay_rubric.md`. |
| `affects_logistics` | `yes` (credible sign that transport, post or last-mile is affected), `unclear` (hazard exists, no sign of parcel impact), `no`. The assessment caps severity at Low for `no` and at Medium for `unclear`. |
| `delay_days_low/high` | Business days, integers. Use `null` if you cannot justify numbers and the script will apply the rubric default and say so. |
| `delay_basis` | Say where the numbers come from: a figure in a source, or your estimate from the rubric. |
| `summary` | Facts only, under 40 words, no numbers that are not in a source. |
| `customer_message` | One plain sentence for the customer. No blame, no drama, no promises. |
| `confidence` | `high` only with an official source or two independent credible sources. |
| `verified` | `true` only if you opened every cited source. |
| `affected_destinations` | Keys from `destinations.json`, format `City|ISO2`. |
| `sources` | At least one per finding. Real URLs you opened, with publisher and publication date. |

Every destination in `destinations.json` must appear in `destinations_checked`. Orders for destinations that are missing are reported as **Not checked**, never as on track.
