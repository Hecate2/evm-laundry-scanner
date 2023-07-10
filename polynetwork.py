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
    fetched_addresses = set()
addresses_to_fetch = queue.Queue()
try:
    with open('addresses_to_fetch.txt', 'r') as f:
        for line in f:
            addresses_to_fetch.put(line.replace('\n', ''))
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


def fetch_transactions(address):
    # Fetch the list of transactions for the given address
    transactions = fetch_asset_transfers_from_address(address)
    fetched_addresses.add(address)
    if transactions is None:
        return

    for tx in transactions:
        if tx['hash'] in fetched_txs:
            continue
        fetched_txs.add(tx['hash'])
        if int(tx['blockNum'], 16) >= 17660325:
            print('\r', end='')
            output_string = f"{tx['hash']} {tx['value']} {tx['asset']} from {tx['from']} to {tx['to']}\n"
            print(output_string, end='')
            output.write(output_string)
            output.flush()
        else:
            print('\r', end='')
            print(f"{addresses_to_fetch.qsize()} addr in queue; Omitting {tx['hash']} at block {int(tx['blockNum'], 16)}", end='')
        if tx['to'] not in fetched_addresses:
            addresses_to_fetch.put(tx['to'])


# Starting Ethereum address
starting_address = '0xe0Afadad1d93704761c8550F21A53DE3468Ba599'
# Fetch transactions recursively
addresses_to_fetch.put(starting_address)

try:
    while not addresses_to_fetch.empty():
        current_address = addresses_to_fetch.get()
        if current_address not in fetched_addresses:
            fetch_transactions(current_address)
except:
    with open('fetched_txs.pkl', 'wb') as f:
        pickle.dump(fetched_txs, f)
    with open('fetched_addresses.pkl', 'wb') as f:
        pickle.dump(fetched_addresses, f)
    with open('addresses_to_fetch.txt', 'w') as f:
        while not addresses_to_fetch.empty():
            f.write(addresses_to_fetch.get() + '\n')
        f.write(current_address + '\n')
