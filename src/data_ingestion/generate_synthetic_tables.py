"""
Generates the customer, device, and merchant tables — the supporting cast
around our transactions. Deliberately includes real-world messiness
(inconsistent country names, some missing device links) so later cleaning
work is genuine, not just for show.
"""

import random
import uuid

from faker import Faker
import psycopg2

fake = Faker()

CUSTOMER_COUNT = 2000
MERCHANT_COUNT = 300
DEVICE_MISSING_RATE = 0.10

MERCHANT_CATEGORIES =       ['retial','grocery','travel','utility','gambling','crypto_exchange','p2p_transfer']
MERCHANT_CATEGORY_WEIGHTS = [ 0.30,     0.20,     0.10,    0.15,   0.05,   0.05,   0.15]


COUNTRY_VARIANTS = {
    'US': ['USA','United States','US'],
    'UK': ['UK','United Kingdom'],
    'IN': ['India','IN'],
}
COUNTRY_WEIGHTS = [0.5, 0.2, 0.3]


def _new_id(prefix: str) -> str:
    return f"{prefix}{str(uuid.uuid4().int)[:9]}"


def generate_devices(n=int(CUSTOMER_COUNT * (1- DEVICE_MISSING_RATE))):
    devices = []
    for _ in range(n):
        devices.append({
            'device_id': _new_id('D'),
            'device_type': random.choice(['mobile','desktop','tablet']),
            'operating_system': random.choice(['iOS','Android','Windows','macOS']),
            'is_rooted_or_jailbroken': random.random() < 0.03,
        })
    return devices


def generate_customers(devices: list):
    device_ids = [d['device_id'] for d in devices]
    customers = []
    for _ in range(CUSTOMER_COUNT):
        real_country = random.choices(list(COUNTRY_VARIANTS.keys()), weights = COUNTRY_WEIGHTS, k=1)[0]
        home_country = random.choice(COUNTRY_VARIANTS[real_country])

        has_device = random.random() > DEVICE_MISSING_RATE
        customers.append({
            'customer_id': _new_id('C'),
            'full_name': fake.name(),
            'signup_date': fake.date_between(start_date='-5y', end_date = '-30d'),
            'home_country': home_country,
            'kyc_risk_score': round(random.uniform(0,1),2),
            'device_id': random.choice(device_ids) if has_device else None,
        })
    return customers



def generate_merchants():
    merchants = []
    for _ in range(MERCHANT_COUNT):
        merchants.append({
            'merchant_id': _new_id('M'),
            'merchant_name': fake.company(),
            'merchant_category': random.choices(MERCHANT_CATEGORIES, weights=MERCHANT_CATEGORY_WEIGHTS,k=1)[0],
        })
    return merchants


def load_to_postgres(devices,customers,merchants):
    conn = psycopg2.connect(host='127.0.0.1', port=5433, dbname='frauddb',
                            user='fraud_admin', password='fraud_pass')
    with conn.cursor() as cur:
        for d in devices:
            cur.execute(
                """INSERT INTO staging.devices (device_id, device_type, operating_system, is_rooted_or_jailbroken)
                   VALUES (%(device_id)s, %(device_type)s, %(operating_system)s, %(is_rooted_or_jailbroken)s)
                   ON CONFLICT (device_id) DO NOTHING""", d)

        for c in customers:
            cur.execute(
                """INSERT INTO staging.customers (customer_id, full_name, signup_date, home_country, kyc_risk_score, device_id)
                   VALUES (%(customer_id)s, %(full_name)s, %(signup_date)s, %(home_country)s, %(kyc_risk_score)s, %(device_id)s)
                   ON CONFLICT (customer_id) DO NOTHING""", c)

        for m in merchants:
            cur.execute(
                """INSERT INTO staging.merchants (merchant_id, merchant_name, merchant_category)
                   VALUES (%(merchant_id)s, %(merchant_name)s, %(merchant_category)s)
                   ON CONFLICT (merchant_id) DO NOTHING""", m)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print('Generating devices')
    devices = generate_devices()
    print(f'{len(devices)} devices created')

    print('generating customers')
    customers = generate_customers(devices)
    missing = sum(1 for c in customers if c['device_id'] is None)
    print(f'{len(customers)} customers created ({missing} with no device on file).')

    print('generating merchants')
    merchants = generate_merchants()
    print(f'{len(merchants)} merchants created')

    print('Loading everything into Postgres...')
    load_to_postgres(devices,customers,merchants)
    print('Done.')

