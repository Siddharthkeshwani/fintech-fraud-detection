"""
The Kafka Consumer — catches each transaction envelope off the Kafka belt
and stores it neatly onto the shelf (the staging.transactions table in Postgres).
"""

import json 


from kafka import KafkaConsumer
import psycopg2


TOPIC_NAME = "transactions"
BOOTSTRAP_SERVERS = ["localhost:9092"]

INSERT_SQL = """
INSERT INTO staging.transactions
    (step, type, amount, name_orig, oldbalance_org, newbalance_orig,
     name_dest, oldbalance_dest, newbalance_dest, is_fraud, event_time)
VALUES (%(step)s, %(type)s, %(amount)s, %(nameOrig)s, %(oldbalanceOrg)s, %(newbalanceOrig)s,
        %(nameDest)s, %(oldbalanceDest)s, %(newbalanceDest)s, %(is_fraud)s, %(event_time)s)
"""


def build_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_deserializer= lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="fraud_detection_group",
    )

def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5433,
        dbname="frauddb",
        user="fraud_admin",
        password="fraud_pass",
    )


def insert_transaction(conn, txn: dict):
    with conn.cursor() as cur:
        cur.execute(INSERT_SQL, txn)
    conn.commit()


def run():
    consumer = build_consumer()
    conn = get_connection()
    print(f"Consumer started. Listening on topic '{TOPIC_NAME}'...\n")
    try:
        for message in consumer:
            txn = message.value
            insert_transaction(conn, txn)

            flag = "<-- FRAUD" if txn['is_fraud'] else ""
            print(f"[STORED] step {txn['step']:<5} {txn['type']:9s} "
                  f"${txn['amount']:>10,.2f} {txn['nameOrig']} -> {txn['nameDest']}{flag}")
            
    except KeyboardInterrupt:
        print("\nStopping Consumer...")
    finally:
        consumer.close()
        conn.close()
        print("Consumer closed cleanly")

if __name__== "__main__":
    run()