// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract EllipticCurve {

    // The field order for the elliptic curve operations
    uint256 internal constant FIELD_ORDER = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;
    uint256 internal constant GEN_ORDER = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;

    // Elliptic curve parameters for the G1 point
    struct G1Point {
        uint256 X;
        uint256 Y;
    }

    // Generator point for G1
    G1Point internal G1 = G1Point(1, 2);

    // Function to check if two G1Points are equal
    function isEqual(G1Point memory a, G1Point memory b) internal pure returns (bool) {
        return a.X == b.X && a.Y == b.Y;
    }

    // Implementations for elliptic curve operations (addition and scalar multiplication)
    function add(G1Point memory p1, G1Point memory p2) internal view returns (G1Point memory r) {
        uint[4] memory input = [p1.X, p1.Y, p2.X, p2.Y];
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 6, input, 0xc0, r, 0x60)
            switch success case 0 {invalid()}
        }
        require(success);
    }

    function multiply(G1Point memory p, uint256 s) internal view returns (G1Point memory r) {
        uint[3] memory input = [p.X, p.Y, s];
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 7, input, 0x80, r, 0x60)
            switch success case 0 {invalid()}
        }
        require(success);
    }
}
