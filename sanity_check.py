from src.data_ingestion.transaction_generator import generate_transaction, _make_customer_pool, _make_merchant_pool

customers, merchants = _make_customer_pool(), _make_merchant_pool()

txns = [generate_transaction(i, customers, merchants) for i in range(5000)]

fraud_count = sum(t["is_fraud"] for t in txns)

print(f"{fraud_count} fraud out of {len(txns)} ({fraud_count/len(txns)*100:.3f}%)")