import web3

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
BOLD = "\033[1m"

def deploy_contract(abi: str, bytecode: str, PROVIDER: str, PRIVATE_KEY: str, ADDRESS: str, CHAIN_ID: str = "1337"):
    """
    Deploys a contract to the blockchain

    Args:
        abi (str): ABI of the contract
        bytecode (str): Bytecode of the contract
        PROVIDER (str): URL of the blockchain node
        PRIVATE_KEY (str): Private key of the account that will deploy the contract
        ADDRESS (str): Address of the account that will deploy the contract
    """

    print("\n"+BOLD+"+"*20 + " DEPLOYMENT " + "+"*20+RESET+"\n")
    # Connect to blockchain node
    w3 = web3.Web3(web3.Web3.HTTPProvider(PROVIDER))
    if(w3.is_connected() == False):
        print(f"{BOLD}[DEPLOYMENT]{RESET} {RED}Could not connect to blockchain node.{RESET}")
        exit(1)
    else:
        print(f"{BOLD}[DEPLOYMENT]{RESET} Connected to blockchain node.")
    # Set the account
    account = {"private_key": PRIVATE_KEY, "address": ADDRESS}

    # Create the contract
    contract = w3.eth.contract(
        abi=abi, bytecode=bytecode
    )
    # Submit the transaction that deploys the contract
    construct_txn = contract.constructor().build_transaction({
        "chainId": int(CHAIN_ID),
        "gasPrice": w3.eth.gas_price,
        "from": account["address"],
        "nonce": w3.eth.get_transaction_count(account["address"]),
    })

    print(f"{BOLD}[DEPLOYMENT]{RESET} Gas price : " + str(w3.eth.gas_price))
    print(f"{BOLD}[DEPLOYMENT]{RESET} Gas estimate : " + str(contract.constructor().estimate_gas()))
    print(f"{BOLD}[DEPLOYMENT]{RESET} Deploying contract...")

    # Sign the transaction
    tx_create = w3.eth.account.sign_transaction(construct_txn, account["private_key"])
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    print(f"{BOLD}[DEPLOYMENT]{RESET} Waiting for transaction to finish...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"{BOLD}[DEPLOYMENT]{RESET} {GREEN}{BOLD}Contract deployed at address: {tx_receipt.contractAddress}{RESET}")
    print(f"{BOLD}[DEPLOYMENT]{RESET} {BOLD}Paste this address to client.{RESET}")
