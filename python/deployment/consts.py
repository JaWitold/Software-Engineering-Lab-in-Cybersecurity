from py_ecc.typing import Point2D
import os
GANACHE_URL = "HTTP://127.0.0.1:7545"
CHAIN_ID = 1337
SOL_VER = "0.8.18"

SOL_CONTRACT_NAME = "SchnorrSignature"
SOL_CONTRACT_FILENAME = SOL_CONTRACT_NAME + ".sol"

SOL_ELIPTIC_CURVE_NAME = "EllipticCurve"
SOL_ELIPTIC_CURVE_FILENAME = SOL_ELIPTIC_CURVE_NAME + ".sol"

_abi_json_filename = "abi.json"
_curr_file = os.path.abspath(__file__)
_deployment_dir = os.path.dirname(_curr_file)
_python_dir = os.path.dirname(_deployment_dir)
_root_dir = os.path.dirname(_python_dir)
_contracts_folder = os.path.join(_root_dir, "contracts")

SOL_CONTRACT_FILE_PATH = os.path.join(_contracts_folder, SOL_CONTRACT_FILENAME)
SOL_ELIPTIC_CURVE_FILE_PATH = os.path.join(
    _contracts_folder, SOL_ELIPTIC_CURVE_FILENAME)
ABI_FILENAME = os.path.join(_deployment_dir, _abi_json_filename)


def bn128Point_to_list(point: Point2D):
    return [point[0].n, point[1].n]
