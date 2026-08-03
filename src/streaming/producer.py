"""
The Kafka Producer — takes each transaction our generator robot creates
and places it gently onto the Kafka conveyor belt (the 'transactions' topic).
Now sourcing REAL customer/merchant IDs from Postgres instead of inventing new ones.
"""

import time
import random
import json

from kafka import KafkaProducer

from src.data_ingestion.transaction_generator import generate_transaction
from src.data_ingestion.db_helpers import load_customer_ids,load_merchant_ids


TOPIC_NAME = "transactions"
BOOTSTRAP_SERVERS = ["localhost:9092"]

def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )


def run():
    producer = build_producer()
    customers = load_customer_ids()
    merchants = load_merchant_ids()
    step = 0

    print(f"Producer started with {len(customers)} real customers and "
          f"{len(merchants)} real merchants. Sending to '{TOPIC_NAME}'...\n")
    try:
        while True:
            txn = generate_transaction(step,customers,merchants)
            producer.send(TOPIC_NAME,value=txn)

            flag = "<-- FRAUD" if txn['is_fraud'] else ""
            print(f"[SENT] step {txn['step']:<5} {txn['type']:9s} "
                  f"${txn['amount']:>10,.2f} {txn['nameOrig']} -> {txn['nameDest']}{flag}")
            step +=1
            time.sleep(random.uniform(0.2,1.0))
    except KeyboardInterrupt:
        print("\nStopping producer...")

    finally:
        producer.flush()
        producer.close()
        print('Producer closed cleanly.')


if __name__== "__main__":
    run()


        
        