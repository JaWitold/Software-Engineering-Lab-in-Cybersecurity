"""
This module provides functions to perform keccak256 hashing and to replicate
Solidity's abi.encodePacked functionality in Python.

Functions:
    keccak256(arg): Computes the keccak256 hash of a single argument.
    The argument should be a byte string.

    encode_packed(*args): Replicates Solidity's abi.encodePacked function.
    It takes any number of arguments, which can be uint256 integers, floats
    or strings, and encodes them into a concatenated byte string without
    padding.

The module uses the `eth_api` library to handle byte-level conversions
and the `Crypto.Hash` library to compute keccak256 hashes.

Example:
    The module can be used to encode multiple arguments into a byte string and
    then compute their keccak256 hash. The hash can be further processed as
    needed, such as applying a modulus to convert it into a specific integer
    range.
"""

from Crypto.Hash import keccak
from eth_abi import encode

def keccak256(arg):
    """Compute the keccak256 hash of the given arguments."""
    hasher = keccak.new(digest_bits=256)

    hasher.update(arg)
    return hasher.digest()


def encode_packed(*args):
    """
    Replicates Solidity's `abi.encodePacked`. This function takes any number
    of uint256 arguments and encodes them as a concatenated byte string.
    """
    types = []
    values = []

    for arg in args:
        if isinstance(arg, int):
            # Handle integers
            types.append('uint256')
            values.append(arg)
        elif isinstance(arg, str):
            # Handle strings (you must decide on the encoding)
            types.append('bytes32')
            values.append(arg.encode('utf-8'))
            # Add other data types as needed

    return encode(types, values)


if __name__ == "__main__":
    # Define the uint256 values
    X_0 = 0x1234  # Example uint256 value
    X_1 = 0x6789  # Example uint256 value
    MESSAGE = 0x1222  # Example uint256 value

    # Perform the encoding
    encoded_packed_bytes = encode_packed(X_0, X_1, MESSAGE)
    print(encoded_packed_bytes.hex())

    # Compute the hash
    hash_bytes = keccak256(encoded_packed_bytes)

    # Convert hash to integer and apply modulus
    GEN_ORDER = 0x30644E72E131A029B85045B68181585D2833E84879B9709143E1F593F0000001
    h = int.from_bytes(hash_bytes, byteorder="big") % GEN_ORDER
    print(h)
