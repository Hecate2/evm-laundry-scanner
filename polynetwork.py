from copy import copy
import json
import pickle
import queue
# from web3 import Web3
import requests

# Connect to an Ethereum node
url = 'https://eth-mainnet.g.alchemy.com/v2/_ki9mpf_eLMuhMmHxDTDm62gmS9yRZrD'
# w3 = Web3(Web3.HTTPProvider(url))
session = requests.Session()

try:
    with open('fetched_txs.pkl', 'rb') as f:
        fetched_txs = pickle.load(f)
except:
    fetched_txs = set()
try:
    with open('fetched_addresses.pkl', 'rb') as f:
        fetched_addresses = pickle.load(f)
except:
    fetched_addresses = dict()
addresses_to_fetch = dict()
starting_address = '0xe0Afadad1d93704761c8550F21A53DE3468Ba599'
addresses_to_fetch[starting_address] = []
try:
    with open('addresses_to_fetch.pkl', 'rb') as f:
        addresses_to_fetch = pickle.load(f)
except:
    pass
output = open('results.txt', 'a')



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
            raise ValueError("Error: No result found in the response.")
    else:
        raise ValueError(f"Error: Request failed with status code {response.status_code}.")


def fetch_transactions(address, route=None):
    if route is None:
        route = []
    # Fetch the list of transactions for the given address
    transactions = fetch_asset_transfers_from_address(address)
    fetched_addresses[address] = route
    if transactions is None:
        return

    for tx in transactions:
        if tx['hash'] in fetched_txs:
            continue
        fetched_txs.add(tx['hash'])
        if int(tx['blockNum'], 16) >= 17660325:
            print('\r', end='')
            output_string = f"{tx['hash']} {tx['value']} {tx['asset']} from {tx['from']} to {tx['to']}; route {route}\n"
            print(output_string, end='')
            # output.write(f"{tx['hash']},{tx['value']},{tx['asset']},{tx['from']},{tx['to']}\n")
            output.write(output_string)
            output.flush()
        else:
            print('\r', end='')
            print(f"{len(addresses_to_fetch)} addr in queue; Omitting {tx['hash']} at block {int(tx['blockNum'], 16)}", end='')
        if tx['to'] not in fetched_addresses:
            copy_route = copy(route)
            copy_route.append(tx['hash'])
            addresses_to_fetch[tx['to']] = copy_route
    return [tx['hash'] for tx in transactions]


try:
    while addresses_to_fetch:
        current_address = next(iter(addresses_to_fetch))
        current_route = addresses_to_fetch[current_address]
        del addresses_to_fetch[current_address]
        if current_address not in fetched_addresses:
            txs = fetch_transactions(current_address, route=current_route)
except:
    with open('fetched_txs.pkl', 'wb') as f:
        pickle.dump(fetched_txs, f)
    with open('fetched_addresses.pkl', 'wb') as f:
        pickle.dump(fetched_addresses, f)
    with open('addresses_to_fetch.pkl', 'wb') as f:
        addresses_to_fetch[current_address] = current_route
        pickle.dump(addresses_to_fetch, f)
