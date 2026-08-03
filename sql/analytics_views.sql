CREATE SCHEMA  IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.customer_transaction_360 AS
WITH velocity AS (
    SELECT
        t.*,
        COUNT(*) OVER (PARTITION BY t.name_orig
                       ORDER BY t.step
                       RANGE BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS txns_last_3_hours
    FROM staging.transactions t
),
clean_customers AS (
    select
         customer_id,
         full_name,
         signup_date,
         kyc_risk_score,
         device_id,
        CASE
            WHEN home_country IN ('USA','United States','US') THEN 'US'
            WHEN home_country IN ('UK','United Kingdom') THEN 'UK'
            WHEN home_country IN ('India','IN') THEN 'IN'
            ELSE home_country
         END AS home_country_clean
        FROM staging.customers
)
SELECT
    v.*,
    c.full_name AS customer_name,
    c.home_country_clean AS home_country,
    c.kyc_risk_score,
    d.device_type,
    d.operating_system,
    d.is_rooted_or_jailbroken,
    m.merchant_category
FROM velocity v
LEFT JOIN clean_customers c ON v.name_orig = c.customer_id
LEFT JOIN staging.devices d ON c.device_id = d.device_id
LEFT JOIN staging.merchants m ON v.name_dest = m.merchant_id;



CREATE OR REPLACE VIEW analytics.unified_transactions AS
SELECT
    'internal_generator' AS source_system,
    id::text AS source_transaction_id,
    event_time::date AS transaction_date,
    type AS transaction_type,
    amount,

    name_dest AS counterparty,
    is_fraud
FROM staging.transactions

UNION ALL

SELECT
    'plaid_sandbox' AS source_system,
    transaction_id AS source_transaction_id,
    date AS transaction_date,
    payment_channel AS transaction_type,
    amount,
    merchant_name AS counterparty,
    NULL AS is_fraud
FROM staging.plaid_transactions;
