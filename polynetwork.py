from web3 import Web3
import requests
import json

# Connect to an Ethereum node
url = 'https://eth-mainnet.g.alchemy.com/v2/_ki9mpf_eLMuhMmHxDTDm62gmS9yRZrD'
w3 = Web3(Web3.HTTPProvider(url))
session = requests.Session()

fetched_txs = set()

def fetch_asset_transfers_from_address(address):
    # Alchemy API request payload
    payload = {
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": '0x10c92e2',
                "category": ["external", "erc20", "erc721"],
                "fromAddress": address,
            }
        ],
        "id": 0
    }

    # Send POST request to Alchemy API
    response = session.post(url, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if 'result' in result:
            txs = result['result']['transfers']
            # for transfer in transfers:
            #     # Print the details of the asset transfer
            #     print(f"Asset Transfer: From {transfer['from']} to {transfer['to']}")
            #     print(f"Asset Type: {transfer['assetType']}")
            #     print(f"Asset Value: {transfer['value']}")
            return [t for t in txs if t['from'].lower() == address.lower()]
        else:
            print("Error: No result found in the response.")
    else:
        print(f"Error: Request failed with status code {response.status_code}.")


def fetch_transactions(address):
    # Fetch the list of transactions for the given address
    transactions = fetch_asset_transfers_from_address(address)
    if transactions is None:
        return

    for tx in transactions:
        if tx['hash'] in fetched_txs:
            continue
        fetched_txs.add(tx['hash'])
        if int(tx['blockNum'], 16) >= 17660325:
            print(f"[{tx['hash']}] {tx['value']} {tx['asset']} from {tx['from']} to {tx['to']}")
        else:
            print('\r', end='')
            print(f"Omitting {tx['hash']} at block {int(tx['blockNum'], 16)}", end='')
        fetch_transactions(tx['to'])


# Starting Ethereum address
starting_address = '0xe0Afadad1d93704761c8550F21A53DE3468Ba599'
# Fetch transactions recursively
fetch_transactions(starting_address)