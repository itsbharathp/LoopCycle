# LoopCycle Nusantara — Dataset Reference

**Organisation:** LoopCycle Nusantara | Bandung, West Java, Indonesia | Founded 2015
**Business:** Waste-to-value social enterprise — formalises informal waste pickers into a traceable recycling supply chain. Buys sorted plastic from 3,500 registered pickers at fair-trade rates, pelletises it, and sells recycled resin to FMCG packaging makers.
**Scale:** 160 staff, 12 collection hubs across West Java | Turnover ~$4.2 M USD
**Data window:** June 2026 – September 2026 (WIB, UTC+7 unless noted)

---

## Folder Structure

```
LoopCycle/
├── Data/
│   ├── CallCentre_Ticket_Data/         # Phone/chat support interactions
│   ├── Comment_Data/                   # Platform reviews and Instagram comments
│   ├── Post_Data/                      # Instagram publishing and audience analytics
│   └── Sales_Data/                     # Tote-bag order and revenue data
│       ├── Abandoned_Carts/            # Checkout funnel and abandoned-cart detail
│       ├── loopcycle_tote_daily_sales.csv
│       ├── loopcycle_tote_orders.csv
│       ├── loopcycle_tote_post_sales_lift.csv
│       ├── shopify_abandoned_checkouts.csv    # duplicate of Abandoned_Carts/
│       └── instagram_abandoned_conversations.csv  # duplicate of Abandoned_Carts/
├── loop-tote-site/                     # Static marketing site (HTML)
└── Prestentations/                     # Slide decks
```

> **Note on duplicates:** `shopify_abandoned_checkouts.csv` and `instagram_abandoned_conversations.csv` appear both directly under `Sales_Data/` and inside `Sales_Data/Abandoned_Carts/`. The files are identical — use either copy.

---

## CallCentre\_Ticket\_Data

> Path: `Data/CallCentre_Ticket_Data/`

### `loopcycle_call_centre_log.csv` — 26 rows

Call-by-call log of every inbound phone call routed through the call centre.

| Column | Type | Description |
|---|---|---|
| `call_id` | string | Unique call identifier |
| `call_start_wib` | datetime | Call start time (WIB) |
| `direction` | string | Always `Inbound` in this extract |
| `queue` | string | IVR queue the call landed in |
| `ivr_path` | string | Key-press path taken through IVR menu |
| `caller_type` | string | Customer segment (consumer, picker, B2B, etc.) |
| `caller_number_masked` | string | Masked MSISDN |
| `wait_time_sec` | integer | Seconds in queue before agent answered |
| `talk_time_sec` | integer | Seconds of active conversation |
| `hold_time_sec` | integer | Seconds placed on hold |
| `agent` | string | Agent name |
| `transfers` | integer | Number of transfers during the call |
| `disposition` | string | Outcome: `Resolved on call`, `Ticket created`, `Callback scheduled`, `Abandoned` |
| `ticket_id` | string | Linked support ticket (if created) |
| `caller_sentiment` | string | Agent-assessed sentiment (see distribution below) |
| `call_summary` | string | Free-text summary written by agent |
| `qa_score` | float | Quality-assurance score (0–100) |
| `callback_required` | boolean | Whether a callback was promised |

**Caller sentiment distribution:**
| Sentiment | Count |
|---|---|
| Neutral | 10 |
| Frustrated | 7 |
| Angry | 7 |
| Satisfied | 2 |

**Disposition distribution:** Ticket created 12 · Callback scheduled 6 · Resolved on call 6 · Abandoned 2

---

### `loopcycle_support_tickets.csv` — 37 rows

Master ticket record covering all support channels. Date range: 2026-06-03 to 2026-09-27.

| Column | Type | Description |
|---|---|---|
| `ticket_id` | string | Unique ticket ID |
| `created_at_wib` | datetime | Ticket creation timestamp |
| `channel` | string | Origin channel (Phone, WhatsApp, Email, Web form, Instagram DM, Marketplace chat) |
| `requester_type` | string | Customer type |
| `requester_id` | string | Anonymised requester ID |
| `subject` / `description` | string | Ticket title and body |
| `category` | string | Issue category (see distribution below) |
| `priority` | string | Normal / High / Low / Urgent |
| `status` | string | Closed / Solved / Pending / Escalated |
| `assigned_team` / `assigned_agent` | string | Routing |
| `related_order_id` / `platform` / `hub` / `b2b_account` | string | Context references |
| `first_response_at` / `first_response_minutes` | datetime / integer | First-response SLA |
| `resolved_at` / `resolution_hours` | datetime / float | Resolution SLA |
| `sla_first_response_min` / `sla_resolution_hours` | integer | SLA targets |
| `sla_breached` | boolean | Whether any SLA was missed |
| `reopen_count` / `escalation_level` | integer | Post-resolution quality signals |
| `root_cause` / `resolution_summary` | string | Free-text root cause and resolution |
| `compensation_type` / `compensation_idr` | string / integer | Goodwill compensation offered |
| `csat_score` | float | Post-resolution satisfaction score (1–5) |
| `tags` | string | Comma-separated topic tags |
| `related_call_id` | string | Link to `call_centre_log` |

**Priority:** Normal 23 · High 9 · Low 4 · Urgent 1
**Status:** Closed 20 · Solved 13 · Pending 3 · Escalated 1
**SLA breached:** No 25 · Yes 12 (32% breach rate)
**Top categories:** Delivery delay 5 · Damaged packaging 4 · Product quality 3 · Order cancelled 2 · Payment issue 2 · Refund/return 2 · Picker payment delay 2 · Wrong item sent 2

---

### `loopcycle_support_ticket_messages.csv` — 155 rows

Threaded conversation messages attached to support tickets.

| Column | Type | Description |
|---|---|---|
| `ticket_id` | string | Foreign key to `support_tickets.csv` |
| `message_time_wib` | datetime | Message timestamp |
| `author_type` | string | `agent` or `requester` |
| `author` | string | Name or anonymised ID |
| `message` | string | Message body |

---

## Comment\_Data

> Path: `Data/Comment_Data/`

All review and comment files include two model-generated columns:
- **`synthetic_sentiment_label`** — `positive` / `neutral` / `negative` / `unrelated` / `n/a`
- **`synthetic_topic`** — topic tag applied to each comment (e.g. `quality`, `delivery_delay`, `sustainability`)

### `loopcycle_instagram_comments.csv` — 1,515 rows

All comments and replies on LoopCycle's Instagram posts. Date range: 2026-08-01 to 2026-09-28.

| Column | Type | Description |
|---|---|---|
| `comment_id` | string | Instagram comment ID |
| `media_id` | string | Parent post ID |
| `post_tag` | string | Short label for the post (e.g. `tote_drop_sep`) |
| `parent_comment_id` | string | Populated for replies; null for top-level comments |
| `text` | string | Comment text |
| `timestamp` | datetime | UTC timestamp |
| `username` | string | Commenter handle |
| `like_count` | integer | Likes on the comment |
| `hidden` | boolean | Whether LoopCycle hid the comment |
| `is_brand_reply` | boolean | `true` if this is an official LoopCycle response |

**Sentiment distribution (1,515 comments):**
| Sentiment | Count | % |
|---|---|---|
| positive | 513 | 34% |
| neutral | 413 | 27% |
| n/a (brand replies) | 352 | 23% |
| unrelated | 145 | 10% |
| negative | 92 | 6% |

**Top topics:** brand_reply 352 · quiz_guess 146 · support_local 113 · excitement 102 · design 72 · sustainability 67 · where_to_buy 59 · tag_friend 55

---

### `loopcycle_reviews_shopee.csv` — 127 rows

Product reviews exported from Shopee seller dashboard.

| Column | Type | Description |
|---|---|---|
| `order_sn` | string | Shopee order serial number |
| `item_id` | string | Product listing ID |
| `model_name` | string | SKU variant (colour/size) |
| `rating_star` | integer | Star rating 1–5 |
| `comment` | string | Review text |
| `buyer_username` | string | Anonymised buyer handle |
| `create_time` | datetime | Review submission time |
| `like_count` | integer | Helpful votes |
| `media_count` | integer | Attached photos/videos |
| `seller_reply` / `reply_time` | string / datetime | Merchant response |

**Sentiment:** positive 72 (57%) · unrelated 28 (22%) · negative 17 (13%) · neutral 10 (8%)
**Top topics:** quality 39 · appearance 19 · usability 19 · sustainability 9 · delivery_delay 8

---

### `loopcycle_reviews_shopify_website.csv` — 93 rows

Reviews collected via the LoopCycle Shopify storefront (verified buyers).

| Column | Type | Description |
|---|---|---|
| `review_id` | string | Internal review ID |
| `product_handle` / `product_title` | string | Product identifier |
| `rating` | integer | Star rating 1–5 |
| `review_title` / `review_body` | string | Review content |
| `reviewer_display_name` | string | Display name |
| `review_date` | date | Submission date |
| `verified_buyer` | boolean | Whether purchase was verified |
| `order_name` | string | Linked order |
| `photo_count` | integer | Attached images |
| `merchant_reply` / `reply_date` | string / date | Store response |
| `review_status` | string | Published / hidden |
| `featured` | boolean | Pinned to homepage |

**Sentiment:** positive 62 (67%) · neutral 14 (15%) · unrelated 10 (11%) · negative 7 (8%)
**Top topics:** quality 30 · appearance 17 · sustainability 16 · usability 9 · size 7

---

### `loopcycle_reviews_tokopedia.csv` — 46 rows

Reviews from Tokopedia marketplace.

| Column | Type | Description |
|---|---|---|
| `invoice_number` | string | Tokopedia invoice ID |
| `product_id` / `product_name` / `variant_name` | string | Product reference |
| `rating` | integer | 1–5 |
| `review_message` | string | Review text |
| `reviewer_name` | string | Display name |
| `review_time` | datetime | Submission timestamp |
| `helpful_count` | integer | Upvotes |
| `attachment_count` | integer | Photos attached |
| `seller_response` / `response_time` | string / datetime | Merchant reply |

**Sentiment:** positive 22 (48%) · unrelated 10 (22%) · negative 8 (17%) · neutral 6 (13%)

---

### `loopcycle_reviews_google_store.csv` — 33 rows

Google Maps reviews for LoopCycle's physical store/hub.

| Column | Type | Description |
|---|---|---|
| `review_id` | string | Google review ID |
| `place_name` | string | Location name |
| `star_rating` | integer | 1–5 |
| `review_text` | string | Review body |
| `reviewer_name` | string | Google profile name |
| `local_guide` | boolean | Whether reviewer is a Local Guide |
| `photo_count` | integer | Photos attached |
| `likes` | integer | Helpful votes |
| `review_time` | string | Relative or absolute timestamp |
| `owner_response` / `owner_response_date` | string / date | Business reply |

**Sentiment:** positive 21 (64%) · neutral 9 (27%) · unrelated 2 (6%) · negative 1 (3%)
**Top topics:** service 18 · location 6 · stock 4 · quality 3

---

### `loopcycle_reviews_lazada.csv` — 24 rows

Lazada marketplace reviews with dual seller/delivery ratings.

| Column | Type | Description |
|---|---|---|
| `order_number` | string | Lazada order ID |
| `sku_id` | string | Product SKU |
| `product_rating` / `seller_rating` / `delivery_rating` | integer | 1–5 per dimension |
| `review_title` / `review_content` | string | Review text |
| `buyer_nickname` | string | Anonymised handle |
| `review_date` | date | Submission date |
| `likes` | integer | Helpful votes |
| `has_images` | boolean | Photo attached |
| `verified_purchase` | boolean | Purchase verified |
| `seller_reply` | string | Merchant response |

**Sentiment:** positive 14 (58%) · negative 4 (17%) · neutral 4 (17%) · unrelated 2 (8%)

---

### `loopcycle_reviews_amazon.csv` — 13 rows

Amazon.com / Amazon.sg product reviews.

| Column | Type | Description |
|---|---|---|
| `review_id` / `asin` | string | Review and product identifiers |
| `reviewer_id` / `reviewer_name` | string | Reviewer reference |
| `rating` | integer | 1–5 |
| `review_title` / `review_text` | string | Review content |
| `review_date` | date | Submission date |
| `review_location` | string | Country of reviewer |
| `variation` | string | Colour/size variant |
| `verified_purchase` | boolean | Purchase verified |
| `helpful_votes` | integer | Helpful votes |
| `vine_program` | boolean | Amazon Vine reviewer |
| `image_count` | integer | Photos attached |
| `amazon_order_id` | string | Linked order |

**Sentiment:** unrelated 5 (38%) · positive 4 (31%) · neutral 3 (23%) · negative 1 (8%)

---

### `loopcycle_reviews_blibli.csv` — 8 rows

Reviews from Blibli marketplace.

| Column | Type | Description |
|---|---|---|
| `order_no` | string | Blibli order number |
| `product_sku` | string | SKU |
| `rating` | integer | 1–5 |
| `recommended` | boolean | Buyer would recommend |
| `review_content` | string | Review text |
| `reviewer` | string | Display name |
| `review_date` | date | Submission date |
| `photo_count` | integer | Photos attached |
| `merchant_reply` | string | Merchant response |

**Sentiment:** positive 5 (63%) · unrelated 3 (38%)

---

### `loopcycle_reviews_tiktok_shop.csv` — 14 rows

Reviews from TikTok Shop.

| Column | Type | Description |
|---|---|---|
| `order_id` / `product_id` / `sku_id` | string | Order and product references |
| `review_rating` | integer | 1–5 |
| `review_content` | string | Review text |
| `reviewer_nickname` | string | TikTok handle |
| `review_create_time` | datetime | Submission timestamp |
| `review_media_count` | integer | Media attached |
| `has_video` | boolean | Video review |
| `like_count` | integer | Likes |
| `is_verified_purchase` | boolean | Purchase verified |
| `seller_reply` / `seller_reply_time` | string / datetime | Merchant response |

**Sentiment:** positive 8 (57%) · unrelated 4 (29%) · neutral 2 (14%)

---

### Cross-platform sentiment summary

| Platform | Rows | Positive | Neutral | Negative | Unrelated |
|---|---|---|---|---|---|
| Instagram comments | 1,515 | 34% | 27% | 6% | 33% (n/a + unrelated) |
| Shopee | 127 | 57% | 8% | 13% | 22% |
| Shopify website | 93 | 67% | 15% | 8% | 11% |
| Tokopedia | 46 | 48% | 13% | 17% | 22% |
| Google Store | 33 | 64% | 27% | 3% | 6% |
| Lazada | 24 | 58% | 17% | 17% | 8% |
| TikTok Shop | 14 | 57% | 14% | 0% | 29% |
| Amazon | 13 | 31% | 23% | 8% | 38% |
| Blibli | 8 | 63% | 0% | 0% | 38% |

> **`synthetic_sentiment_label`** and **`synthetic_topic`** are model-generated fields. `unrelated` typically indicates the text is not about the product (emoji-only, spam, tagging, etc.). `n/a` in Instagram data marks official brand replies.

---

## Post\_Data

> Path: `Data/Post_Data/`

### `loopcycle_instagram_posts_flat.csv` — 30 rows

One row per Instagram post with organic performance metrics.

| Column | Type | Description |
|---|---|---|
| `id` | string | Instagram media ID |
| `timestamp` | datetime | Post publish time (UTC) |
| `media_type` | string | `IMAGE`, `CAROUSEL_ALBUM`, `REEL` |
| `media_product_type` | string | `FEED` or `REELS` |
| `content_pillar` | string | Editorial category (see below) |
| `permalink` | string | Public URL |
| `caption` | string | Post caption |
| `reach` | integer | Unique accounts reached |
| `views` | integer | Total views (Reels only meaningful) |
| `likes` / `comments` / `shares` / `saved` | integer | Engagement counts |
| `total_interactions` | integer | Sum of all engagements |
| `follows` | integer | New follows from this post |
| `profile_visits` | integer | Profile visits attributed |
| `ig_reels_avg_watch_time` | float | Average watch time in seconds (Reels) |
| `ig_reels_video_view_total_time` | float | Total watch time in minutes (Reels) |
| `engagement_rate_by_reach_pct` | float | `total_interactions / reach × 100` |
| `reels_skip_rate` | float | Share of viewers who skipped (Reels) |

**Content pillar distribution:** loop_tote 8 · picker_stories 6 · process_impact 6 · behind_the_scenes 5 · education 3 · b2b_partners 2

---

### `loopcycle_post_kpis.csv` — 30 rows

Extended per-post KPI table (44 columns). Includes all columns from `instagram_posts_flat.csv` plus:

| Additional columns | Description |
|---|---|
| `timestamp_utc` / `post_weekday_wib` / `post_hour_wib` | Publish timing breakdowns |
| `post_age_days` | Days since published (at extract time) |
| `caption_length_chars` / `hashtag_count` | Caption metadata |
| `audience_*` modelled fields | Estimated age, gender, and location breakdown for each post's reached audience |
| Reel performance fields | `reels_avg_watch_pct`, `reels_completion_rate`, `reels_skip_rate` |

---

### `loopcycle_post_views_time.csv` — 1,132 rows

Distribution of views by time-since-publish for each post. Useful for decay-curve analysis.

| Column | Type | Description |
|---|---|---|
| `post_id` | string | Foreign key to post tables |
| `dimension` | string | Type of time bucket (e.g. `hours_since_post`) |
| `bucket` | string | Time range label (e.g. `0-1h`, `1-3h`) |
| `views` | integer | Views in that bucket |
| `share_pct_of_views` | float | Share of total post views |
| `data_source` | string | API endpoint or model |

---

### `loopcycle_post_audience_age_gender.csv` — 630 rows

Per-post reached-audience breakdown by age group and gender.

| Column | Type | Description |
|---|---|---|
| `post_id` | string | Foreign key to post tables |
| `age` | string | Age group: `13-17`, `18-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65+` |
| `gender` | string | `M`, `F`, `U` (undisclosed) |
| `value` | integer | Count of accounts |
| `share_pct_of_reach` | float | Percentage of total post reach |
| `data_source` | string | Data source label |

---

### `loopcycle_post_audience_location.csv` — 1,920 rows

Per-post reached-audience breakdown by country, province, and city.

| Column | Type | Description |
|---|---|---|
| `post_id` | string | Foreign key to post tables |
| `level` | string | `country`, `province_state`, or `city` |
| `country` | string | ISO country code |
| `province_state` | string | Province/state name |
| `city` | string | City name |
| `region_group` | string | Derived macro-region |
| `value` | integer | Count of accounts reached |
| `share_pct_of_reach` | float | Share of total post reach |

**Top countries reached:** Indonesia (ID) · Malaysia (MY) · Australia (AU) · Singapore (SG) · Netherlands (NL)
**Top cities:** Bandung, Jakarta, Surabaya, Bekasi, Depok, Tangerang, Bogor

---

### `loopcycle_audience_age_gender.csv` — 105 rows

Account-level audience snapshot (not per-post) — overall followers, reached, and engaged audiences.

| Column | Type | Description |
|---|---|---|
| `audience_type` | string | `followers`, `reached`, `engaged` |
| `timeframe` | string | Snapshot period |
| `age` | string | Age group (7 bands: 13-17 through 65+) |
| `gender` | string | `M`, `F`, `U` |
| `value` | integer | Count of accounts |
| `share_pct_of_audience` | float | Percentage within audience type |
| `data_source` | string | Data source label |

---

### `loopcycle_audience_location.csv` — 195 rows

Account-level audience snapshot broken down by geography.

| Column | Type | Description |
|---|---|---|
| `audience_type` | string | `followers`, `reached`, `engaged` |
| `timeframe` | string | Snapshot period |
| `level` | string | `country`, `city` |
| `country` | string | ISO country code |
| `city` | string | City name |
| `value` | integer | Count of accounts |
| `share_pct_of_audience` | float | Percentage within audience type |
| `province_state_derived` / `region_group_derived` | string | Enriched geography fields |

---

## Sales\_Data

> Path: `Data/Sales_Data/`

### `loopcycle_tote_daily_sales.csv` — 1,071 rows

Daily aggregated sales by platform. Date range: 2026-06-01 to 2026-09-27 (119 days × 9 channels).

| Column | Type | Description |
|---|---|---|
| `date` | date | Calendar date |
| `weekday` | string | Day of week |
| `channel_group` | string | High-level channel (e.g. Indonesian marketplace, Website) |
| `platform` | string | Specific platform (Shopee, Tokopedia, TikTok Shop, Lazada, Blibli, Amazon, Website (Shopify), Instagram (DM/WhatsApp), Physical store) |
| `orders` | integer | Orders placed that day on that platform |
| `units_sold` | integer | Units sold |
| `order_total_idr` | integer | Gross revenue in IDR |
| `gross_profit_idr` | integer | Gross profit in IDR |
| `loop_tote_ig_post_that_day` | boolean | Whether an Instagram post went live that day |
| `ig_post_ids` | string | Comma-separated post IDs published that day |

**Total orders across all platforms:** 2,867

---

### `loopcycle_tote_orders.csv` — 2,867 rows

Individual order-level records. Date range: 2026-06-01 to 2026-09-27.

| Column | Type | Description |
|---|---|---|
| `order_id` | string | Unique order identifier (e.g. `#LT10001`) |
| `order_datetime_wib` | datetime | Full order timestamp (WIB) |
| `order_date` / `weekday` | date / string | Date and day of week |
| `channel_group` / `platform` | string | Sales channel group and specific platform |
| `sku` / `product_name` / `colour_variant` | string | Product SKU, name, and colour |
| `order_type` | string | `standard`, `bulk`, etc. |
| `quantity` / `unit_price_idr` | integer | Units and per-unit price |
| `gross_amount_idr` | integer | `quantity × unit_price_idr` before discounts |
| `discount_idr` / `promo_code` | integer / string | Discount applied and code used |
| `shipping_fee_paid_idr` | integer | Shipping charged to customer |
| `order_total_idr` | integer | Final amount paid by customer |
| `platform_fee_idr` / `payment_fee_idr` / `cogs_idr` | integer | Cost components |
| `gross_profit_idr` | integer | `order_total - platform_fee - payment_fee - cogs` |
| `original_currency` / `original_order_total` / `usd_idr_rate` | string / float | Multi-currency fields (populated for Amazon/international orders) |
| `payment_method` | string | Payment type (e.g. ShopeePay, bank transfer) |
| `courier` | string | Delivery carrier (e.g. J&T Express) |
| `customer_id` | string | Anonymised customer ID |
| `customer_type` | string | `new` or `returning` |
| `customer_city` / `customer_province_state` / `customer_country` | string | Buyer location |
| `status` | string | Order status (e.g. `completed`) |
| `ship_date` / `delivered_date` | date | Fulfilment timeline |
| `traffic_source` / `utm_campaign` | string | Acquisition source and campaign |
| `attributed_ig_post_id` / `attribution_basis` | string | Instagram post attribution |
| `campaign` | string | Promotional campaign label |

**Colour variant distribution:**
| Variant | Orders |
|---|---|
| Sea-green | 1,069 (37%) |
| Indigo | 726 (25%) |
| Sand | 617 (22%) |
| Batik Kawung | 234 (8%) |
| Batik Parang | 215 (7%) |
| Assorted | 6 (<1%) |

**Channel distribution:** Indonesian marketplace 903 · Website (Shopify) 898 · Instagram 606 · Physical store 357 · Amazon 103

---

### `loopcycle_tote_post_sales_lift.csv` — 8 rows

Modelled sales-lift attribution linking Instagram posts to order spikes.

| Column | Type | Description |
|---|---|---|
| `post_id` | string | Instagram post ID |
| `post_tag` | string | Short descriptive label |
| `format` | string | Post format (Feed, Reel, Carousel) |
| `ig_reach` | integer | Unique accounts reached by post |
| `expected_orders_per_day_baseline` | float | Baseline daily orders (pre-post average) |
| `orders_0_24h` / `lift_pct_0_24h` | integer / float | Orders and % lift in first 24 hours |
| `orders_24_72h` / `lift_pct_24_72h` | integer / float | Orders and % lift in 24–72 h window |
| `orders_0_7d` | integer | Cumulative orders in 7-day window |
| `modeled_attributed_orders` | integer | Modelled orders attributable to the post |
| `top_channel_group_0_72h` | string | Channel with highest lift in 0–72 h |

---

## Sales\_Data / Abandoned\_Carts

> Path: `Data/Sales_Data/Abandoned_Carts/`

Files covering checkout and conversation drop-off across every sales channel.

### `shopify_abandoned_checkouts.csv` — 1,326 rows

One row per abandoned Shopify checkout. Date range: 2026-06-01 to 2026-09-27.

| Column | Type | Description |
|---|---|---|
| `checkout_id` | string | Shopify checkout token |
| `created_at_wib` / `updated_at_wib` | datetime | Checkout open and last-activity timestamps |
| `customer_id` | string | Shopify customer ID (blank for guest) |
| `customer_email_masked` / `customer_phone_masked` | string | Masked contact details |
| `accepts_marketing` | boolean | Whether customer opted into marketing |
| `device_type` | string | `mobile`, `desktop`, `tablet` |
| `customer_city` / `customer_province_state` / `customer_country` | string | Buyer location |
| `sku` / `product_name` / `colour_variant` / `quantity` | string / integer | Cart contents |
| `subtotal_idr` / `discount_idr` / `shipping_quote_idr` / `total_idr` | integer | Pricing breakdown |
| `discount_code` | string | Voucher code entered |
| `checkout_stage_reached` | string | Furthest step: `contact_info`, `shipping_method`, `payment_method_selected`, `payment_attempted_failed` |
| `payment_method_selected` / `payment_failure_code` | string | Payment details |
| `traffic_source` / `utm_campaign` / `attributed_ig_post_id` / `landing_page` | string | Acquisition and attribution |
| `session_duration_sec` / `pages_viewed` | integer | Session behaviour |
| `modeled_abandonment_reason` | string | Model-assigned drop-off reason (see distribution below) |
| `recovery_email_1_*` / `recovery_email_2_*` | string / boolean | Recovery email send and open/click flags |
| `whatsapp_reminder_sent_at` / `whatsapp_replied` | datetime / boolean | WhatsApp recovery touchpoint |
| `recovery_status` | string | `abandoned` or `recovered` |
| `recovery_channel` | string | Channel that recovered the order |
| `recovered_order_id` / `recovered_at_wib` | string / datetime | Linked completed order |
| `abandoned_checkout_url` | string | Shopify recovery URL |
| `attribution_basis` | string | How attribution was determined |

**Recovery status:** abandoned 1,228 (93%) · recovered 98 (7%)

**Abandonment stage:** shipping_method 402 · payment_method_selected 374 · contact_info 325 · payment_attempted_failed 225

**Top modelled abandonment reasons:** unexpected_shipping_cost 226 · payment_failed 225 · distracted_or_session_ended 163 · just_browsing_or_comparing 104 · site_slow_or_error 91 · payment_page_expired 89 · waiting_for_voucher 84 · checking_marketplace_price 81 · delivery_time_too_long 80

---

### `instagram_abandoned_conversations.csv` — 979 rows

One row per Instagram DM/WhatsApp sales conversation that did not convert. Date range: 2026-06-01 to 2026-09-27.

| Column | Type | Description |
|---|---|---|
| `conversation_id` | string | Internal conversation ID |
| `first_message_at_wib` / `last_message_at_wib` | datetime | Conversation open and close timestamps |
| `entry_point` | string | How the conversation started: `direct_dm`, `story_reply`, `whatsapp_click`, `comment_to_dm` |
| `attributed_ig_post_id` | string | Post that triggered the conversation |
| `inquiry_type` | string | `price`, `availability`, `colour_options`, `shipping`, `bulk_order` |
| `sku_interest` / `colour_interest` / `quantity_interest` | string / integer | Product interest expressed |
| `quoted_total_idr` | integer | Price quoted to customer |
| `stage_reached` | string | Furthest step: `inquiry_only`, `quote_sent`, `payment_details_sent`, `address_collected`, `payment_proof_pending` |
| `agent_first_reply_minutes` | integer | Minutes to first agent response |
| `agent` | string | Agent name |
| `messages_in_thread` | integer | Total messages exchanged |
| `followup_sent` / `followup_count` | boolean / integer | Whether and how many follow-ups were sent |
| `status` | string | `abandoned` or `recovered` |
| `recovered_order_id` / `recovered_at_wib` | string / datetime | Linked completed order |
| `modeled_abandonment_reason` | string | Model-assigned drop-off reason |
| `data_source` / `attribution_basis` | string | Data provenance |

**Status:** abandoned 907 (93%) · recovered 72 (7%)

**Top inquiry types:** price 332 · availability 258 · colour_options 190 · shipping 155 · bulk_order 44

**Top entry points:** direct_dm 552 · story_reply 183 · whatsapp_click 165 · comment_to_dm 79

**Top abandonment reasons:** price_concern 221 · slow_agent_reply 189 · wanted_different_colour_or_sold_out 114 · shipping_cost 113 · just_asking_no_intent 110 · manual_bank_transfer_friction 88

---

### `shopify_checkout_funnel_daily.csv` — 119 rows

Daily Shopify website funnel aggregates (one row per day). Date range: 2026-06-01 to 2026-09-27.

| Column | Type | Description |
|---|---|---|
| `date` / `weekday` | date / string | Calendar date |
| `sessions` / `sessions_from_instagram` | integer | Total and Instagram-attributed sessions |
| `product_page_views` | integer | Product detail page views |
| `add_to_cart_sessions` | integer | Sessions that added to cart |
| `checkouts_started` | integer | Checkouts initiated |
| `orders_completed` | integer | Successful orders |
| `orders_from_recovered_checkouts` | integer | Orders from recovery campaigns |
| `abandoned_checkouts_total` | integer | Total abandoned checkouts |
| `abandoned_checkouts_in_recovery_export` | integer | Subset with contact info captured |
| `abandoned_without_contact_info` | integer | Abandons with no recovery path |
| `gross_checkout_abandonment_rate_pct` | float | `abandoned / started × 100` |
| `net_checkout_abandonment_rate_pct` | float | After excluding no-contact-info rows |
| `ig_post_published_within_40h` | boolean | Instagram post live within 40 h of date |

---

### `shopee_product_funnel_daily.csv` — 119 rows

Daily Shopee product-page funnel (one row per day). Date range: 2026-06-01 to 2026-09-27.

| Column | Type | Description |
|---|---|---|
| `date` / `item_id` | date / string | Date and Shopee product ID |
| `product_visitors` / `product_page_views` | integer | Traffic to listing |
| `visitors_added_to_cart` / `units_added_to_cart` | integer | Add-to-cart activity |
| `visitors_placed_order` / `orders_placed` / `orders_paid` | integer | Conversion steps |
| `orders_unpaid_expired` | integer | Placed but not paid (expired) |
| `conversion_rate_pct` | float | Visitors → paid orders |
| `derived_cart_abandonment_pct` | float | Cart adds that did not convert |

---

### `tokopedia_product_funnel_daily.csv` — 119 rows

Daily Tokopedia product funnel. Same date range as Shopee.

| Column | Type | Description |
|---|---|---|
| `date` / `product_id` | date / string | Date and Tokopedia product ID |
| `product_views` / `unique_visitors` | integer | Traffic |
| `cart_additions` / `wishlist_additions` | integer | Consideration signals |
| `buyers` / `orders` | integer | Conversion |
| `conversion_pct` / `derived_cart_abandonment_pct` | float | Funnel rates |

---

### `lazada_product_funnel_daily.csv` — 119 rows

Daily Lazada product funnel (PDP = product detail page).

| Column | Type | Description |
|---|---|---|
| `date` / `sku_id` | date / string | Date and Lazada SKU |
| `pdp_views` / `pdp_visitors` | integer | Traffic |
| `add_to_cart_visitors` / `add_to_cart_units` / `wishlist_adds` | integer | Consideration |
| `buyers` / `orders` | integer | Conversion |
| `conversion_pct` / `derived_cart_abandonment_pct` | float | Funnel rates |

---

### `blibli_product_funnel_daily.csv` — 119 rows

Daily Blibli product funnel (simplified — fewer funnel steps than other platforms).

| Column | Type | Description |
|---|---|---|
| `date` / `product_sku` | date / string | Date and Blibli SKU |
| `page_views` / `visitors` | integer | Traffic |
| `add_to_cart` / `orders` | integer | Consideration and conversion |
| `derived_cart_abandonment_pct` | float | Cart adds that did not convert |

---

### `tiktok_shop_product_funnel_daily.csv` — 357 rows

Daily TikTok Shop funnel split by traffic source (3 sources × 119 days = 357 rows).

| Column | Type | Description |
|---|---|---|
| `date` / `product_id` / `traffic_source` | date / string | Date, product, and source (Video, Search, Showcase) |
| `product_impressions` / `product_page_views` | integer | Top-of-funnel |
| `add_to_cart_users` / `orders` | integer | Conversion |
| `conversion_pct` / `derived_cart_abandonment_pct` | float | Funnel rates |

---

### `amazon_traffic_daily.csv` — 119 rows

Daily Amazon traffic and sales report (Business Reports style).

| Column | Type | Description |
|---|---|---|
| `date` / `asin` | date / string | Date and Amazon product ASIN |
| `sessions_browser` / `sessions_mobile_app` / `sessions_total` | integer | Session counts by device |
| `page_views` | integer | Product page views |
| `featured_offer_buy_box_pct` | float | % of time in Buy Box |
| `units_ordered` / `unit_session_pct` | integer / float | Orders and conversion rate |
| `ordered_product_sales_usd` | float | Revenue in USD (Amazon reports in USD) |

---

## Notes

- **Currency:** All monetary values are in **IDR (Indonesian Rupiah)** unless noted. Approximate rate: 1 USD ≈ 15,800 IDR at time of data capture. `amazon_traffic_daily.csv` is the exception — Amazon reports in USD.
- **Timestamps:** Fields suffixed `_wib` are in **WIB (UTC+7)**. Fields suffixed `_utc` are UTC. Instagram API timestamps are UTC.
- **Synthetic fields:** `synthetic_sentiment_label` and `synthetic_topic` are generated by an LLM and may contain classification errors, particularly for short or multilingual (Bahasa Indonesia / English mix) text.
- **`unrelated` sentiment:** Covers emoji-only posts, friend tags, spam, and comments that do not express a product opinion.
- **`n/a` sentiment** (Instagram only): Reserved for official brand/LoopCycle replies where sentiment scoring is not meaningful.
- **Duplicate files:** `shopify_abandoned_checkouts.csv` and `instagram_abandoned_conversations.csv` exist both under `Sales_Data/` and `Sales_Data/Abandoned_Carts/` — files are byte-for-byte identical.
- **Presentations folder:** `Prestentations/` contains slide decks (`.pptx`) and is not part of the data pipeline.
- **Data is synthetic/simulated** and generated to represent realistic operations of LoopCycle Nusantara for analytics development and demonstration purposes.
