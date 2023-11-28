from typing import List, Tuple

from py_ecc.fields import bn128_FQ
from py_ecc.typing import Point2D

from schnorr_signature import SchnorrSignature
from py_ecc.bn128.bn128_curve import multiply, add, G1
from util import encode_packed, randsn
import json


class NodeRingSignature:
    def __init__(self, schnorr_signature: SchnorrSignature, ring: list[Tuple[bn128_FQ, bn128_FQ]]):
        self.ss = schnorr_signature
        self.ring = ring

    def sign(self, privkey: int, message: int) -> dict:
        """[DEPRECATED] I'll delete this function soon.
        Sign a message using a node ring signature.

        Args:
            privkey (int): Private key.
            message (int): Message to be signed.

        Returns:
            Tuple[Tuple[int, int], int]: Signature of the message.
        """

        public_key = multiply(G1, privkey)
        if(not public_key):
            raise ValueError("Public key not found.")

        position = self.ring.index(public_key)

        if position < 0 or position >= len(self.ring):
            raise ValueError("Invalid position")

        pubkey, signature = self.ss.sign(privkey, message)
        if(not signature[0]):
            raise ValueError("Signature is None.")

        d = {
            "signature": {
                "x_": list([int(elt) for elt in signature[0]]),
                "s": int(signature[1]),
            },
        }
        return d

    def parse_signature(self, d: dict) -> Tuple[Tuple[bn128_FQ, bn128_FQ], int]:
        """[DEPRECATED] I'll delete this function soon.
        Parse a signature.

        Args:
            d (dict): Signature to be parsed.

        Returns:
            Tuple[bn128_FQ, bn128_FQ]: Parsed signature.
        """

        t = tuple(d["signature"]["x_"])
        signature = ((bn128_FQ(t[0]), bn128_FQ(t[1])), d["signature"]["s"])
        return signature


    def verify(self, message: int, signature: Tuple[Tuple[bn128_FQ, bn128_FQ], int]) -> bool:
        """[DEPRECATED] I'll delete this function soon.
        Verify a node ring signature.

        Args:
            message (int): Message corresponding to the signature.
            signature (Tuple[Tuple[bn128_FQ, bn128_FQ], int]): Signature to be verified.

        Returns:
            bool: True if the signature is valid, else False.
        """

        verif = [
            self.ss.verify(public_key, message, signature) for public_key in self.ring
        ]

        return any(verif)


    def generate_pairwise_different_random_values(self, n: int, random_values: List[int] = []) -> List[int]:
        """
        Generate n pairwise different random values.

        Args:
            n (int): Number of random values to generate.
            random_values (List[int]): List of random values generated so far.

        Returns:
            List[int]: List of n pairwise different random values.
        """
        if random_values is None:
            random_values = []

        while len(random_values) < n:
            random_value = randsn()
            if random_value not in random_values:
                random_values.append(random_value)

        return random_values

    def r_sign(self, privkey: int, message: int, public_keys: List[Tuple[bn128_FQ,bn128_FQ]]) -> dict:
        """
        Generate a node ring signature.

        Args:
            privkey (int): Private key of the current signer.
            message (int): Message to be signed.
            public_keys (List[Tuple[bn128_FQ,bn128_FQ]]): List of public keys in the ring excluding the current signer's public key.

        Returns:
            dict: Node ring signature components.
        """

        aa = self.generate_pairwise_different_random_values(len(public_keys))
        rr = [multiply(G1, ai) for ai in aa]
        rr = [ri for ri in rr if ri is not None]

        hh = [self.ss.hash(encode_packed(r_[0].n, r_[1].n, message)) for r_ in rr]

        temp = G1
        for y_i, h_i in zip(public_keys, hh):
            m = multiply(y_i, h_i)
            temp = add(temp, m)

        while True:
            ax = randsn()
            cond = False
            rx = add(multiply(G1, ax), temp)

            for r_i in rr:
                if rx == r_i:
                    cond = True
                    break

            zero = bn128_FQ.zero()
            if not rx == (zero, zero) and not cond:
                break

        hx = self.ss.hash(encode_packed(rx[0].n, rx[1].n, message))
        s = 0
        for a_i in aa:
            s += a_i
        s += ax + privkey * hx

        index = randsn() % len(public_keys)
        rr.insert(index, rx)

        public_key = multiply(G1, privkey)
        public_keys.insert(index, public_key)

        # returning dict instead of json because solidity don't support tuples
        return {
                "rr": list([(elt[0].n, elt[1].n) for elt in rr]),
                "s": int(s),
                "public_keys": list([[elt[0].n, elt[1].n] for elt in public_keys]),
            }

    def parse_r_signature(self, d: dict) -> Tuple[List[Tuple[bn128_FQ, bn128_FQ]], int, List[Tuple[bn128_FQ, bn128_FQ]]]:
        """
        Parse a node ring signature.

        Args:
            d (dict): Node ring signature to be parsed.

        Returns:
            Tuple[List[Tuple[bn128_FQ, bn128_FQ]], int, List[int]]: Parsed node ring signature.
        """

        rr = tuple([tuple(elt) for elt in d["rr"]])
        s = d["s"]
        public_keys = [(bn128_FQ(t[0]), bn128_FQ(t[1])) for t in d["public_keys"]]
        return rr, s, public_keys

    def r_verify(self, message: int, signature: dict) -> bool:
        """
        Verify a node ring signature.

        Args:
            message (int): Message corresponding to the signature.
            signature (Tuple[List[Tuple[bn128_FQ, bn128_FQ]], int, List[int]]): Node ring signature components.

        Returns:
            bool: True if the signature is verified, else False.
        """

        print("message=", message)
        print("signature=", json.dumps(signature, indent=2))
        signature = self.parse_r_signature(signature)

        rr, s, public_keys = signature


        return False


def test1():
    """
    [DEPRECATED] I'll delete this function soon.
    """

    PRIVATE_KEYS_RING = [
        19977808579986318922850133509558564821349392755821541651519240729619349670944,
        34783947491279721981739821
    ]

    PUBLIC_KEYS_RING = [multiply(G1, key) for key in PRIVATE_KEYS_RING]

    MESSAGE = 123
    position = 0

    schnorr_signature = SchnorrSignature()
    node_ring_signature = NodeRingSignature(schnorr_signature, PUBLIC_KEYS_RING)

    d_signature = node_ring_signature.sign(PRIVATE_KEYS_RING[position], MESSAGE)
    signature = node_ring_signature.parse_signature(d_signature)
    assert node_ring_signature.verify(MESSAGE, signature)
    assert not node_ring_signature.verify(MESSAGE + 1, signature)
    print("Test 1 passed successfully.")


def test2():
    PRIVATE_KEYS_RING = [
        19977808579986318922850133509558564821349392755821541651519240729619349670944,
        34783947491279721981739821
        ]

    PUBLIC_KEYS_RING = [multiply(G1, key) for key in PRIVATE_KEYS_RING]

    MESSAGE = 123
    position = 0
    PUBLIC_KEYS_RING_WITHOUT_SIGNER = [key for key in PUBLIC_KEYS_RING if key != PUBLIC_KEYS_RING[position]]

    schnorr_signature = SchnorrSignature()
    node_ring_signature = NodeRingSignature(schnorr_signature, PUBLIC_KEYS_RING)

    s = node_ring_signature.r_sign(PRIVATE_KEYS_RING[position], MESSAGE, PUBLIC_KEYS_RING_WITHOUT_SIGNER)
    assert node_ring_signature.r_verify(MESSAGE, s)


if __name__ == "__main__":
    test1()
    test2()



