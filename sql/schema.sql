CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.transactions (
    id      SERIAL PRIMARY KEY,
    step    INT NOT NULL,
    type    VARCHAR(20) NOT NULL,
    amount  NUMERIC(14,2) NOT NULL,
    name_orig  VARCHAR(50) NOT NULL,
    oldbalance_org  NUMERIC(14,2),
    newbalance_orig NUMERIC(14,2),
    name_dest       VARCHAR(50) NOT NULL,
    oldbalance_dest NUMERIC(14,2),
    newbalance_dest NUMERIC(14,2),
    is_fraud        SMALLINT NOT NULL,
    event_time      TIMESTAMP NOT NULL,
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.devices (
    device_id VARCHAR(20) PRIMARY KEY,
    device_type VARCHAR(20),
    operating_system VARCHAR(20),
    is_rooted_or_jailbroken BOOLEAN
);

CREATE TABLE IF NOT EXISTS staging.customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    signup_date DATE NOT NULL,
    home_country VARCHAR(50),
    kyc_risk_score NUMERIC(4,2),
    device_id VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS staging.merchants (
    merchant_id VARCHAR(20) PRIMARY KEY,
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS staging.plaid_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50),
    amount NUMERIC(14,2),
    iso_currency_code VARCHAR(10),
    date DATE,
    merchant_name VARCHAR(150),
    category VARCHAR(100),
    payment_channel VARCHAR(30),
    pending BOOLEAN,
    ingested_at TIMESTAMP DEFAULT NOW()
);
