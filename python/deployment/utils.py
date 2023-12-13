from dotenv import load_dotenv
import os

SOL_ELLIPTIC_CURVE_FILENAME = "EllipticCurve.sol"

# If you don't use the docker container, make sure to change this parameter
ENV_PATH = "/app/.env"

def parse_dot_env() -> tuple[str, str, str, str, str, str, str, str]:
    load_dotenv(ENV_PATH)

    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    if(PRIVATE_KEY == None):
        print("Please set PRIVATE_KEY in .env")
        exit(1)

    ADDRESS = os.getenv("ADDRESS")
    if(ADDRESS == None):
        print("Please set ADDRESS in .env")
        exit(1)

    PROVIDER = os.getenv("PROVIDER_URL")
    if(PROVIDER is None):
        print("Please set PROVIDER_URL in .env")
        exit(1)

    CONTRACTS_PATH = os.getenv("CONTRACTS_PATH", "/app/contracts/")
    CONTRACTS_BUILD_PATH = os.getenv("CONTRACTS_BUILD_PATH", "/app/build/")
    CHAIN_ID = os.getenv("CHAIN_ID", "1337")

    SOLC_VERSION = os.getenv("SOLC_VERSION", "0.8.22")

    FILES_TO_COMPILE = os.getenv("FILES_TO_COMPILE")
    if(FILES_TO_COMPILE is None):
        print("Please set FILES_TO_COMPILE in .env")
        exit(1)

    return PRIVATE_KEY, ADDRESS, PROVIDER, CONTRACTS_PATH, CONTRACTS_BUILD_PATH, CHAIN_ID, SOLC_VERSION, FILES_TO_COMPILE



def main():
    PRIVATE_KEY, ADDRESS, PROVIDER, CONTRACTS_PATH, CONTRACTS_BUILD_PATH, CHAIN_ID, SOLC_VERSION, FILES_TO_COMPILE = parse_dot_env()
    print("[.env] PRIVATE_KEY: " + PRIVATE_KEY)
    print("[.env] ADDRESS: " + ADDRESS)
    print("[.env] PROVIDER_URL: " + PROVIDER)
    print("[.env] CONTRACTS_PATH: " + CONTRACTS_PATH)
    print("[.env] CONTRACTS_BUILD_PATH: " + CONTRACTS_BUILD_PATH)
    print("[.env] CHAIN_ID: " + CHAIN_ID)
    print("[.env] SOLC_VERSION: " + SOLC_VERSION)

if __name__ == "__main__":
    main()
