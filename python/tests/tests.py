"""
Module with tests
"""

from nr_verify.schemas.util import encode_packed, keccak256
from nr_verify.schemas.schnorr_signature import SchnorrSignature

def test_utils():
    """
    Test for utils from schemes
    """
    # Define the uint256 values
    x_0 = 0x1234  # Example uint256 value
    x_1 = 0x6789  # Example uint256 value
    message = 0x1222  # Example uint256 value

    # Perform the encoding
    encoded_packed_bytes = encode_packed(x_0, x_1, message)
    print(encoded_packed_bytes.hex())

    # Compute the hash
    hash_bytes = keccak256(encoded_packed_bytes)

    # Convert hash to integer and apply modulus
    gen_order = 0x30644E72E131A029B85045B68181585D2833E84879B9709143E1F593F0000001
    hash_val = int.from_bytes(hash_bytes, byteorder="big") % gen_order
    print(hash_val)


def test_schnorr_sign():
    """
    Test for schnorr signing scheme
    """
    privkey_1 = 19977808579986318922850133509558564821349392755821541651519240729619349670944
    privkey_2 = 34783947491279721981739821

    message = 123

    pubkey_1, signature_1 = SchnorrSignature.sign(privkey_1, 123)
    pubkey_2, signature_2 = SchnorrSignature.sign(privkey_2, 123)

    assert SchnorrSignature.verify(pubkey_1, message, signature_1)
    assert SchnorrSignature.verify(pubkey_2, message, signature_2)
    assert not SchnorrSignature.verify(pubkey_1, 124, signature_1)
    assert not SchnorrSignature.verify(pubkey_2, 124, signature_2)
    assert not SchnorrSignature.verify(pubkey_1, message, signature_2)
    assert not SchnorrSignature.verify(pubkey_2, message, signature_1)
