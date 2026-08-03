import psycopg2

def get_connection():
    return psycopg2.connect(
        host= '127.0.0.1', port= 5433, dbname= 'frauddb',
        user = 'fraud_admin', password= 'fraud_pass',
    )


def load_customer_ids():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('Select customer_id FROM staging.customers;')
        ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids


def load_merchant_ids():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT merchant_id FROM staging.merchants')
        ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids