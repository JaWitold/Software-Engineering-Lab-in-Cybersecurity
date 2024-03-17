from Crypto.Hash import keccak
from eth_abi import encode


def keccak256(arg: bytes) -> bytes:
    """
    Compute the keccak256 hash of the given argument.

    :param arg: The input data as bytes to be hashed.
    :type arg: bytes
    :return: The keccak256 hash of the input data.
    :rtype: bytes
    """
    hasher = keccak.new(digest_bits=256)
    hasher.update(arg)
    return hasher.digest()


def sol_hash(*args: int) -> int:
    """
    Compute the hash of the given arguments analogous to Solidity's keccak256 applied to abi.encode.
    This function is useful for generating hashes in a manner consistent with Solidity smart contracts,
    especially for Ethereum blockchain applications.

    :param args: Variable number of arguments which can be only integers
                 These are the values to be tightly packed and hashed.
    :type args: int
    :return: The hash of the encoded arguments as an integer.
    :rtype: int
    """
    return int.from_bytes(keccak256(sol_encode(*args)), "big")


def sol_encode(*args: int) -> bytes:
    """
    Replicates Solidity's `abi.encode` functionality in Python. This function encodes any number of
    integers arguments and encodes them as a concatenated byte string.
    The encoding is done based on the assumption that all arguments are uint256, mirroring Solidity's behavior
    of abi.encode.

    :param args: Variable number of arguments to be encoded, supporting integers
    :type args: int
    :return: A bytes object representing the encoding of the input arguments.
    :rtype: bytes
    """
    return encode(
        ["uint256" for _ in args],
        list(args),
    )
