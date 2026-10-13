# Customer and operator wording

`assess_orders.py` writes drafts to `customer_emails.csv` using the standard template below. Edit the wording in `scripts/assess_orders.py` (function `customer_email`) if your brand voice differs.

## Tone

- Plain, calm, specific. No jargon, no dramatic words, no blame.
- State what is happening, the original date, the updated window and what you are doing.
- Do not promise a delivery date. Give a window and say it may change.
- Do not offer refunds, cancellation or compensation unless the business has approved it (`offer_cancellation` config).

## Standard delay notice

Subject: `Update on your {brand} order {order_id}: delivery may be delayed`

```
Hi {first_name},

Thank you for your order ({product}, {order_id}). We are writing because we have seen a disruption that may delay delivery to {city}.

What is happening: {customer_reason}
Original delivery date: {expected_delivery_date}
Updated estimate: between {eta_low} and {eta_high}

What we are doing: {action_for_status}

If you would like to change the delivery address or have any questions, just reply to this email.

We are sorry for the inconvenience and thank you for your patience.

The {brand} team
```

`action_for_status`:

- In-Transit: "We are tracking your parcel with {courier} and will tell you if the estimate changes."
- Packed: "Your order is packed. We are choosing the most reliable route to you and will confirm once it ships."
- Ordered: "We will dispatch your order as soon as it is ready, using the most reliable route available."

## All-clear follow-up (send only when a person approves)

Subject: `Good news: your {brand} order {order_id} is back on schedule`

```
Hi {first_name}, the disruption we told you about in {city} has eased and your order is on track for {expected_delivery_date}. Thank you for waiting.
```

## Operator update (chat or email to the owner)

Lead with the numbers (open orders, at risk, watch), then the table by destination (orders, delay, original and revised delivery, reason, suggested action), then sources, then what could not be verified.
