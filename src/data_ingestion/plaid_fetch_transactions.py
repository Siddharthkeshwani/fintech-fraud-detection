import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_public_token_create_request_options import SandboxPublicTokenCreateRequestOptions
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
import psycopg2


load_dotenv()

configuration =plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": os.environ['PLAID_CLIENT_ID'],
        "secret": os.environ['PLAID_SANDBOX_SECRET'],
    },
)

api_client  = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_dynamic_test_item():
    options = SandboxPublicTokenCreateRequestOptions(override_username="user_transactions_dynamic")
    create_request = SandboxPublicTokenCreateRequest(
    institution_id="ins_109508",
    initial_products=[Products("transactions")],
    options=options,
    )
    public_token = client.sandbox_public_token_create(create_request)['public_token']

    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    access_token = client.item_public_token_exchange(exchange_request)["access_token"]
    return access_token



def fetch_all_transactions(access_token):
    added = []
    cursor = ""
    has_more =True
    while has_more:
        request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
        response = client.transactions_sync(request)
        added.extend([txn.to_dict() for txn in response['added']])
        has_more = response['has_more']
        cursor = response['next_cursor']
    return added


def insert_plaid_transaction(conn,txn:dict):
    category = ", ".join(txn.get("category") or []) if txn.get("category") else None
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO staging.plaid_transactions
                (transaction_id, account_id, amount, iso_currency_code,
                 category, date, name, merchant_name, category, payment_channel, pending,)
            VALUES (%(transaction_id)s, %(account_id)s, %(amount)s, %(iso_currency_code)s,
                    %(category)s, %(date)s, %(name)s,
                    %(merchant_name)s, %(category_id)s, %(payment_channel)s, %(pending)s)
                    ON CONFLICT (transaction_id) DO NOTHING """,
                {
                    "transaction_id": txn["transaction_id"],
                    "account_id": txn["account_id"],
                    "amount": txn["amount"],
                    "iso_currency_code": txn.get("iso_currency_code"),
                    "date": txn["date"],
                    "name": txn["name"],
                    "merchant_name": txn.get("merchant_name") or txn.get("name"),
                    "category": category,
                    "pending": txn.get("pending",False),
                }
        )
    conn.commit()


if __name__ == "__main__":
    print("Creating a Sandbox item and ongoing simulated activity...")
    access_token = create_dynamic_test_item()
    with open(".plaid_access_token", "w") as f:
        f.write(access_token)
    print("Saved to .plaid_dynamic_access_token\n")

    print("fetching all transactions from Plaid...")
    transactions = fetch_all_transactions(access_token)
    print(f" Retrived {len(transactions)} transactions.\n")

    print("Storing them in Postgres...")
    conn = psycopg2.connect(host="localhost",port=5433,dbname="frauddb",
                            user="fraud_admin",password="fraud_pass")
    for txn in transactions:
        insert_plaid_transaction(conn, txn)
    conn.close()
    print("Done.")
