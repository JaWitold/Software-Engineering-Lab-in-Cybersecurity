import struct
from Crypto.Hash import keccak


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
    byte_array = bytearray()
    for arg in args:
        if isinstance(arg, int):
            # Handle integers
            byte_array.extend(struct.pack('I', arg))
        elif isinstance(arg, float):
            # Handle floats
            byte_array.extend(struct.pack('f', arg))
        elif isinstance(arg, str):
            # Handle strings (you must decide on the encoding)
            byte_array.extend(arg.encode('utf-8'))
            # Add other data types as needed
    return byte_array


if __name__ == "__main__":
    # Define the uint256 values
    X_0 = 0x1234  # Example uint256 value
    X_1 = 0x6789  # Example uint256 value
    message = 0x1222  # Example uint256 value

    # Perform the encoding
    encoded_packed_bytes = encode_packed(X_0, X_1, message)
    print(encoded_packed_bytes.hex())

    # Compute the hash
    hash_bytes = keccak256(encoded_packed_bytes)

    # Convert hash to integer and apply modulus
    GEN_ORDER = 0x30644E72E131A029B85045B68181585D2833E84879B9709143E1F593F0000001
    h = int.from_bytes(hash_bytes, byteorder="big") % GEN_ORDER

    print(h)
