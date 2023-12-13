import json
from solcx import compile_standard
import os

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
BOLD = "\033[1m"

def write_abi(abi: str, contract_name: str, CONTRACTS_BUILD_PATH: str) -> None:
    abi_path = os.path.join(CONTRACTS_BUILD_PATH, f"abi_{contract_name}.json")
    with open(abi_path, "w") as file:
        json.dump(abi, file)


def write_bytecode(bytecode: str, contract_name: str, CONTRACTS_BUILD_PATH: str) -> None:
    bytecode_path = os.path.join(CONTRACTS_BUILD_PATH, f"bytecode_{contract_name}")
    with open(bytecode_path, "w") as file:
        file.write(bytecode)

def compile_contract(contract_name: str, SOLC_VERSION: str, CONTRACTS_PATH: str, CONTRACTS_BUILD_PATH: str, SOL_ELLIPTIC_CURVE_FILENAME: str) -> tuple[str, str]:
    """
    Compiles a contract

    Args:
        contract_name (str): Name of the contract to compile
        SOLC_VERSION (str): Version of the solc compiler
        CONTRACTS_PATH (str): Path to the contracts folder
        CONTRACTS_BUILD_PATH (str): Path to the build folder

    Returns:
        tuple[str, str]: ABI and bytecode of the contract
    """

    print("\n"+BOLD+"+"*20 + " COMPILATION " + "+"*20+RESET+"\n")
    file_name = contract_name + ".sol"
    file_path = os.path.join(CONTRACTS_PATH, file_name)
    try:
        file_content = open(file_path).read()
    except FileNotFoundError:
        print(f"[ERROR - COMPILATION] {RED}Smart contract file not found.{RESET} Full path :", file_path)
        exit(1)

    sol_elliptic_curve_path = os.path.join(CONTRACTS_PATH, SOL_ELLIPTIC_CURVE_FILENAME)
    try:
        sol_elliptic_curve_content = open(sol_elliptic_curve_path).read()
    except FileNotFoundError:
        print(f"[ERROR - COMPILATION] {RED}File not found.{RESET} Full path :", sol_elliptic_curve_path)
        exit(1)


    # Solidity source code
    print(f"{BOLD}[COMPILATION]{RESET} Compiling contract...")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {
                file_path: { "content": file_content },
                sol_elliptic_curve_path: { "content": sol_elliptic_curve_content },
            },
            "settings": {
                "outputSelection": {"*": {"*": ["abi", "evm.bytecode", "metadata", "evm.bytecode.sourceMap"]}}
            },
        },
        solc_version=SOLC_VERSION,
    )

    contract = compiled_sol["contracts"][file_path][contract_name]

    print(f"{BOLD}[COMPILATION]{RESET} Contract compiled successfully.")
    # get abi
    abi = contract["abi"]
    # get bytecode
    bytecode = contract["evm"]["bytecode"]["object"]


    print(f"{BOLD}[COMPILATION]{RESET} Saving contract to build folder...")
    write_abi(abi, contract_name, CONTRACTS_BUILD_PATH)
    write_bytecode(bytecode, contract_name, CONTRACTS_BUILD_PATH)

    print(f"{BOLD}[COMPILATION]{RESET} {GREEN}Contract compiled successfully.{RESET}")
    return abi, bytecode
