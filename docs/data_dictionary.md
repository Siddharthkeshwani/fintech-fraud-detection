# Data Dictionary — Fintech Fraud Detection

Owner: Data Analyst role. Feeds into Step 3 (Analyze) as the handoff artifact
closing out Step 2 (Acquire). Update this file any time a table's shape
or known issues change.

## 1. staging.transactions
Source: self-built generator (`src/data_ingestion/transaction_generator.py`) → Kafka → consumer → Postgres.

| Column | Type | Meaning | Notes |
|---|---|---|---|
| id | SERIAL | internal row id | auto-generated |
| step | INT | simulated hour since the world started | a counter, not a real timestamp |
| type | VARCHAR | transaction type | CASH_OUT, PAYMENT, CASH_IN, TRANSFER, DEBIT |
| amount | NUMERIC | transaction amount | |
| name_orig | VARCHAR | paying customer ID | joins to staging.customers.customer_id |
| oldbalance_org | NUMERIC | payer's balance before | |
| newbalance_orig | NUMERIC | payer's balance after | ~60% of fraud rows show a mismatch here — a deliberate signal, not a bug |
| name_dest | VARCHAR | receiving customer or merchant ID | joins to staging.customers or staging.merchants, depending on type |
| oldbalance_dest | NUMERIC | receiver's balance before | |
| newbalance_dest | NUMERIC | receiver's balance after | |
| is_fraud | SMALLINT | 1 if fraud, 0 if not | our only labeled table — this is what any model trains on |
| event_time | TIMESTAMP | when the transaction happened | |
| ingested_at | TIMESTAMP | when it landed in Postgres | compare to event_time to measure pipeline lag |

## 2. staging.customers
Source: Faker-generated (`src/data_ingestion/generate_synthetic_tables.py`).

| Column | Type | Meaning | Notes |
|---|---|---|---|
| customer_id | VARCHAR | primary key | |
| full_name | VARCHAR | customer name | |
| signup_date | DATE | | |
| home_country | VARCHAR | raw country field | messy on purpose — "USA"/"United States"/"US" mean the same thing; cleaned only inside analytics.customer_transaction_360, never in this base table |
| kyc_risk_score | NUMERIC | risk score, 0–1 | |
| device_id | VARCHAR | linked device | ~10% of customers have none on file, by design |

## 3. staging.devices
Source: Faker-generated, same script as above.

| Column | Type | Meaning | Notes |
|---|---|---|---|
| device_id | VARCHAR | primary key | |
| device_type | VARCHAR | mobile / desktop / tablet | |
| operating_system | VARCHAR | | |
| is_rooted_or_jailbroken | BOOLEAN | true for ~3% of devices | a real-world fraud risk signal, kept rare on purpose |

## 4. staging.merchants
Source: Faker-generated, same script as above.

| Column | Type | Meaning | Notes |
|---|---|---|---|
| merchant_id | VARCHAR | primary key | |
| merchant_name | VARCHAR | | |
| merchant_category | VARCHAR | retail / grocery / travel / utility / gambling / crypto_exchange / p2p_transfer | |

## 5. staging.plaid_transactions
Source: Plaid Sandbox API (`src/data_ingestion/plaid_fetch_transactions.py`), live pull, row count varies per run.

| Column | Type | Meaning | Notes |
|---|---|---|---|
| transaction_id | VARCHAR | Plaid's own ID | primary key |
| account_id | VARCHAR | Plaid's simulated test account | not linked to staging.customers — a separate world |
| amount | NUMERIC | | |
| iso_currency_code | VARCHAR | | |
| date | DATE | | |
| merchant_name | VARCHAR | | |
| category | VARCHAR | comma-joined Plaid category tags | |
| payment_channel | VARCHAR | | |
| pending | BOOLEAN | | |
| is_fraud | — | does not exist in this table | Plaid Sandbox has no fraud concept; all fraud analysis stays on staging.transactions |

## 6. analytics.customer_transaction_360 (view)
Built from staging.transactions + staging.customers + staging.devices + staging.merchants.
Adds `txns_last_3_hours` (rolling velocity count) and a cleaned `home_country`.
This is the primary table for any future model training.

## 7. analytics.unified_transactions (view)
Built from staging.transactions UNION ALL staging.plaid_transactions.
Adds `source_system` so every row can be traced back to where it came from.
`is_fraud` is NULL for every Plaid row — expected, not a data gap.

## Known issues / still to clean
- `home_country` has inconsistent spelling in staging.customers; cleaned only in the view, never in the base table.
- ~10% of customers have no `device_id` (staging.customers), by design.
- Plaid data carries no fraud labels and has no link to our customer table.
- `txns_last_3_hours` resets per `name_orig` only — it won't catch the same
  person operating under two different customer IDs, since duplicate
  identity resolution hasn't been built yet.
