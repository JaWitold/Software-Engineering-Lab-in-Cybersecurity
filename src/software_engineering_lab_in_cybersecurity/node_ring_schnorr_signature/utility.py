from Crypto.Hash import keccak
from eth_abi import packed
from py_ecc.fields import bn128_FQ
from py_ecc.fields.field_elements import IntOrFQ


def keccak256(arg: bytes) -> bytes:
    """
    Compute the keccak256 hash of the given argument.

    :param arg: The input data as bytes to be hashed.
    :return: The keccak256 hash of the input data as a bytes object.
    """
    hasher = keccak.new(digest_bits=256)
    hasher.update(arg)
    return hasher.digest()


def sol_hash(*args: IntOrFQ) -> int:
    """
    Compute the hash of the given arguments analogous to Solidity's keccak256 applied to abi.encodePacked.
    This function is useful for generating hashes in a manner consistent with Solidity smart contracts,
    especially for Ethereum blockchain applications.

    :param args: Variable number of arguments which can be integers or py_ecc.fields.bn128_FQ objects.
                 These are the values to be tightly packed and hashed.
    :return: The hash of the encoded arguments as an integer.
    """
    return int.from_bytes(keccak256(encode_packed(*args)), "big")


def encode_packed(*args: IntOrFQ) -> bytes:
    """
    Replicates Solidity's `abi.encodePacked` functionality in Python. This function takes any number of
    arguments, specifically integers or py_ecc.fields.bn128_FQ objects, and encodes them as a concatenated
    byte string. The encoding is done based on the assumption that all arguments are uint256, mirroring
    Solidity's behavior for tightly packed encoding.

    :param args: Variable number of arguments to be encoded. Supports integers and py_ecc.fields.bn128_FQ objects.
    :return: A bytes object representing the tightly packed encoding of the input arguments.
    """
    return packed.encode_packed(
        ["uint256" for _ in args],
        [int(str(arg)) if isinstance(arg, bn128_FQ) else arg for arg in args],
    )
