import random
import time
import uuid
from datetime import datetime


TRANSACTION_TYPES = ["CASH_OUT","PAYMENT","CASH_IN","TRANSFER","DEBIT"]
TYPE_WEIGHTS =      [0.35,      0.34,       0.22,      0.08,      0.01]

# Fraud only rides on these two types - robbers move money out or transfer it
FRAUD_ELIGIBLE_TYPES = ["TRANSFER","CASH_OUT"]
FRAUD_RATE_AMONG_ELIGIBLE = 0.003

CUSTOMER_POOL_SIZE = 2000
MERCHANT_POOL_SIZE = 300


def _make_customer_pool(n=CUSTOMER_POOL_SIZE):
    return [f"C{str(uuid.uuid4().int)[:9]}" for _ in range(n)]

def _make_merchant_pool(n=MERCHANT_POOL_SIZE):
    return [f"M{str(uuid.uuid4().int)[0:9]}" for _ in range(n)]

def _sample_amount(txn_type: str) -> float:
    if txn_type == "TRANSFER":
        return round(random.lognormvariate(mu=8.5,sigma=1.2),2) # Bigger amounts
    return round(random.lognormvariate(mu=6.5,sigma=1.0),2)     # everyday purchases


def generate_transaction(step: int, customers: list, merchants: list) -> dict:
    txn_type = random.choices(TRANSACTION_TYPES,weights=TYPE_WEIGHTS,k=1)[0]
    amount = _sample_amount(txn_type)


    name_orig = random.choice(customers)
    old_balance_org = round(random.lognormvariate(mu=8.0,sigma=1.3),2)

    is_fraud = 0
    if txn_type in FRAUD_ELIGIBLE_TYPES and random.random() < FRAUD_RATE_AMONG_ELIGIBLE:
        is_fraud = 1
        amount = round(old_balance_org * random.uniform(0.85,1.0),2)

    new_balance_orig = max(0.0,round(old_balance_org - amount,2))
    
    if is_fraud and random.random() < 0.6:
        new_balance_orig = old_balance_org

    name_dest = random.choice(merchants if txn_type == "PAYMENT" else customers)
    old_balance_dest = round(random.lognormvariate(mu=7.5,sigma=1.3),2)
    new_balance_dest = round(old_balance_dest + amount,2)

    return {
        "step":step,
        "type":txn_type,
        "amount":amount,
        "nameOrig":name_orig,
        "oldbalanceOrg":old_balance_org,
        "newbalanceOrig":new_balance_orig,
        "nameDest":name_dest,
        "oldbalanceDest":old_balance_dest,
        "newbalanceDest":new_balance_dest,
        "is_fraud":is_fraud,
        "event_time":datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    customers = _make_customer_pool()
    merchants = _make_merchant_pool()
    step = 0
    print("Generating test transactions... Press Ctrl+C to stop.\n")
    try:
        while True:
            txn = generate_transaction(step,customers,merchants)
            flag = "<-- FRAUD" if txn['is_fraud'] else ""
            print(f"[step {txn['step']}] {txn['type']:9s} ${txn['amount']:>10,.2f}"
                  f" {txn['nameOrig']} -> {txn['nameDest']}{flag}")
            step += 1
            time.sleep(random.uniform(0.2,1.0))
    except KeyboardInterrupt:
        print("\nStopped.")

