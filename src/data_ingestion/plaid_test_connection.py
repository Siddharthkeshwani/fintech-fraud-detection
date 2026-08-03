import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

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

create_request = SandboxPublicTokenCreateRequest(
    institution_id="ins_109508",
    initial_products=[Products("transactions")],
)
create_response = client.sandbox_public_token_create(create_request)
public_token =create_response['public_token']
print(f"Got a public_token: {public_token[:25]}...")


exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
exchange_response = client.item_public_token_exchange(exchange_request)
access_token = exchange_response['access_token']
print(f"Got an access_token: {access_token[:25]}...")

with open(".plaid_access_token", "w") as f:
    f.write(access_token)
print("\nSaved access_token to .plaid_access_token - you're connected")
