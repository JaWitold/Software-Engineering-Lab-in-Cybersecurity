import unittest

from conftest import get_random_int
from Crypto.Hash import keccak
from py_ecc.fields import bn128_FQ

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.utility import (
    encode_packed,
    keccak256,
    sol_hash,
)


class TestUtility(unittest.TestCase):
    """
    Unit tests for cryptographic utility functions including keccak256 hashing,
    Solidity-style hash computation with sol_hash, and abi.encodePacked emulation
    with encode_packed. These tests verify the correct behavior of utilities used
    in the node ring Schnorr signature scheme, ensuring compatibility and correctness
    of hash calculations and data encoding as per Solidity and Ethereum standards.
    """

    def test_keccak256(self):
        """
        Test the keccak256 function to ensure it produces the expected hash output
        for a given input string.
        """
        input_data = b"hello"
        expected_output = keccak.new(digest_bits=256).update(b"hello").digest()
        self.assertEqual(
            keccak256(input_data),
            expected_output,
            "keccak256 hash does not match expected output",
        )

    def test_sol_hash(self):
        """
        Test the sol_hash function to verify that it computes the correct hash value
        for a sequence of integer arguments, emulating Solidity's keccak256 hash
        on tightly packed arguments.
        """
        args = [get_random_int() for _ in range(10)]
        packed_data = encode_packed(*args)
        expected_output = int.from_bytes(keccak.new(digest_bits=256).update(packed_data).digest(), "big")
        self.assertEqual(
            sol_hash(*args),
            expected_output,
            "Solidity hash does not match expected output",
        )

    def test_encode_packed(self):
        """
        Test the encode_packed function to ensure it correctly encodes a combination
        of integers and bn128_FQ objects into a byte string, mimicking Solidity's
        abi.encodePacked functionality.
        """
        for _ in range(1000):
            args = (get_random_int(), bn128_FQ(get_random_int()))
            expected_packed_data = b"".join(
                [(arg if isinstance(arg, int) else arg.n).to_bytes(32, "big") for arg in args]
            )
            self.assertEqual(
                encode_packed(*args),
                expected_packed_data,
                "Encoded packed data does not match expected output",
            )


if __name__ == "__main__":
    unittest.main()
