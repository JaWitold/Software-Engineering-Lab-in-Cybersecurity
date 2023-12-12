from py_ecc.bn128 import multiply, G1
from python.nr_verify.schemas.node_ring_schnorr import NodeRingSchnorr

if __name__ == '__main__':
    # Example usage
    PRIVKEY = 34783947491279721981739821
    s = NodeRingSchnorr()
    seal = s.nr_sign(PRIVKEY, 123, [multiply(G1, 2), multiply(G1, 3)])
    # signature = s.nr_sign(PRIVKEY, 123, [])
    print(seal)
    print("result: ", s.nr_verify(123, seal))
    print("result: ", s.nr_verify(1233, seal))
