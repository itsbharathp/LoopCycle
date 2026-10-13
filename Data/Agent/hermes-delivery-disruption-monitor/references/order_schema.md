# Order file columns

Required: `order_id`, `status`, `expected_delivery_date`, and a destination (`destination_city` and `destination_country`, or `customer_city` and `customer_country`). Country should be an ISO 2-letter code (ID, SG, MY, BE, ES, AU, JP, US, GB ...).

Used when present: `destination_province_state`, `destination_latitude`, `destination_longitude`, `platform`, `courier`, `product_name`, `customer_first_name`, `customer_email`, `email_opt_in` (`yes` or `no`), `tracking_number`.

Statuses in scope by default: `Ordered`, `Packed`, `In-Transit`. Anything else (Delivered, Cancelled, Returned) is ignored.

Dates are ISO (`YYYY-MM-DD`). `expected_delivery_date` is the date promised to the customer.
