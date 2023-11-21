from random import randint
from typing import Tuple
from py_ecc.bn128 import multiply, add, curve_order, G1
from util import keccak256, encode_packed

def randsn(): return randint(1, curve_order - 1)
def addmodn(x, y): return (x + y) % curve_order
def mulmodn(x, y): return (x * y) % curve_order

class SchnorrSignature:

    def hash(self, b: bytes) -> int:
        return int.from_bytes(keccak256(b), byteorder="big") % curve_order

    def sign(self, privkey: int, message: int):
        pubkey = multiply(G1, privkey)

        # X = G1 * x
        x = randsn()
        X = multiply(G1, x)

        # h = Hash(X, message)
        h = self.hash(encode_packed(X[0].n, X[1].n, message))

        # s = x + a * h
        s = addmodn(x, mulmodn(privkey, h))

        return pubkey, (X, s)

    def verify(self, pubkey: int, message: int, signature: Tuple[int, int]) -> bool:
        X, s = signature

        # h = Hash(X, message)
        h = self.hash(encode_packed(X[0].n, X[1].n, message))

        # sG = s * G
        sG = multiply(G1, s)

        # hA = h * A
        hA = multiply(pubkey, h)

        # X + hA
        Xha = add(X, hA)

        # Verify that s * G = X + h * A
        return sG == Xha


if __name__ == "__main__":

    ss = SchnorrSignature()

    PRIVKEY_1 = 19977808579986318922850133509558564821349392755821541651519240729619349670944
    PRIVKEY_2 = 34783947491279721981739821

    MESSAGE = 123

    pubkey_1, signature_1 = ss.sign(PRIVKEY_1, 123)
    pubkey_2, signature_2 = ss.sign(PRIVKEY_2, 123)

    assert ss.verify(pubkey_1, MESSAGE, signature_1)
    assert ss.verify(pubkey_2, MESSAGE, signature_2)
    assert not ss.verify(pubkey_1, 124, signature_1)
    assert not ss.verify(pubkey_2, 124, signature_2)
    assert not ss.verify(pubkey_1, MESSAGE, signature_2)
    assert not ss.verify(pubkey_2, MESSAGE, signature_1)
