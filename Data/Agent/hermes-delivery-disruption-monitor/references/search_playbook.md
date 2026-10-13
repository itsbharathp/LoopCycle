# Search playbook (read before Phase 2)

Goal: find **active** disruptions that could slow deliveries to the destinations in `destinations.json`, prove them with sources, and avoid inventing anything.

## 1. Structure every query: where, what, when

- **Where:** city, province or state, country. Use the search groups in `search_plan.md`.
- **What:** one hazard family per query: natural hazards, strikes and unrest, air quality and fires, national logistics (post, courier, airport, port), courier notices.
- **When:** put the current month and year in the query, or "today" or "this week". Never use a year from memory.
- Search in the local language as well for Indonesia (`banjir`, `longsor`, `erupsi`, `demo`, `mogok`, `kebakaran hutan`).
- Stop early: once an official source confirms an event and its impact, do not run every remaining query for that group.

## 2. Source tiers

| Tier | Examples | How to use |
|---|---|---|
| 1. Official | National weather, disaster and volcano agencies (BMKG, BNPB, PVMBG), airport authorities, postal operators, courier notices | One Tier 1 source is enough for `confidence: high` if it describes the impact |
| 2. Established news and wire services | Major national outlets, regional outlets with named authors | Use two independent Tier 2 sources for `high`; one is `medium` |
| 3. Aggregators, social posts, blogs, strike trackers | Wikipedia, travel blogs, social media | Never enough alone. Use only to find a lead, then confirm in Tier 1 or 2 |

Open every source you cite. A search snippet is not a source.

## 3. The four tests before you record a finding

1. **Active:** the event is ongoing or forecast within the delivery window. The source or its latest update is dated within `search_lookback_days` (default 7), unless it is a long-running event with a recent update.
2. **Located:** it affects the destination or the route to it, not just the same country.
3. **Logistics-relevant:** it plausibly affects roads, air, sea, post or last-mile. A hazard with no sign of parcel impact is `affects_logistics: unclear`, with severity Low.
4. **Sourced:** you can cite at least one real URL with a publisher and date.

If a test fails, either record `severity: none` with a note or drop the lead.

## 4. Anti-hallucination rules

- Never write a number (delay days, casualties, hotspots, wave heights) that is not in a source you opened, except the delay estimate, which must be labelled as an estimate in `delay_basis`.
- Do not name an event, agency, alert level or regulation you have not found in a source.
- Do not copy more than a short phrase (under 15 words) from a source. Summarise in your own words.
- If two sources conflict, record both, use the more cautious severity and say so in `summary`.
- If you cannot open a source, set `verified: false` and `confidence: low`.
- If you find nothing, record `no_disruption_found` with the queries tried. Absence of results is not proof of safety, so say "none found" rather than "safe".
- Do not infer a disruption from one social post or one headline snippet.

## 5. Courier and route check

For each courier in the destination group, search for service notices for that area. If a courier suspends or restricts service to the destination, treat it as `affects_logistics: yes`.

## 6. Example finding

See `findings_schema.md`. A good finding names the event, the place, the date of the latest update, what is affected (roads, flights, sea crossing, post), and where the delay range comes from.

## 7. When to stop and ask a person

- A source suggests danger to people (evacuation orders, active unrest with violence) near a destination.
- A High severity finding rests on a single Tier 2 source.
- The destination is in a conflict zone or under sanctions.
