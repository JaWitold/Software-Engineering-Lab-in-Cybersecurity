from solcx import install_solc

RESET = "\033[0m"
BOLD = "\033[1m"

if __name__ == "__main__":
    from compile import compile_contract
    from deploy import deploy_contract
    from utils import parse_dot_env
    from utils import SOL_ELLIPTIC_CURVE_FILENAME
else:
    from deployment.utils import SOL_ELLIPTIC_CURVE_FILENAME
    from deployment.compile import compile_contract
    from deployment.deploy import deploy_contract
    from deployment.utils import parse_dot_env


def main():
    PRIVATE_KEY, ADDRESS, PROVIDER, CONTRACTS_PATH, CONTRACTS_BUILD_PATH, CHAIN_ID, SOLC_VERSION, FILES_TO_COMPILE = parse_dot_env()
    FILES_TO_COMPILE = FILES_TO_COMPILE.split(",")
    install_solc(SOLC_VERSION)

    for contract_name in FILES_TO_COMPILE:
        print(f"\n{BOLD}[CONTRACT] Compiling " + contract_name + f"{RESET}")
        abi, bytecode = compile_contract(contract_name, SOLC_VERSION=SOLC_VERSION, CONTRACTS_PATH=CONTRACTS_PATH, CONTRACTS_BUILD_PATH=CONTRACTS_BUILD_PATH, SOL_ELLIPTIC_CURVE_FILENAME=SOL_ELLIPTIC_CURVE_FILENAME)
        deploy_contract(abi, bytecode, PROVIDER=PROVIDER, PRIVATE_KEY=PRIVATE_KEY, ADDRESS=ADDRESS, CHAIN_ID=CHAIN_ID)
        print("\n"+"-"*80)


if __name__ == "__main__":
    main()
