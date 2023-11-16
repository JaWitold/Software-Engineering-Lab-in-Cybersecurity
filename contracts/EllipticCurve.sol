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
    G1Point internal G1 = G1Point(
        1, // X coordinate
        2  // Y coordinate
    );

    // Implementations for elliptic curve operations (addition and scalar multiplication)
    function mul(G1Point memory p, uint256 s) internal view returns (G1Point memory r) {
        uint[3] memory input;
        input[0] = p.X;
        input[1] = p.Y;
        input[2] = s;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 7, input, 0x80, r, 0x60)
            // Use "invalid" to make gas estimation work
            switch success case 0 {invalid()}
        }
        require(success);
    }

    function add(G1Point memory p1, G1Point memory p2) internal view returns (G1Point memory r) {
        uint[4] memory input;
        input[0] = p1.X;
        input[1] = p1.Y;
        input[2] = p2.X;
        input[3] = p2.Y;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 6, input, 0xc0, r, 0x60)
            // Use "invalid" to make gas estimation work
            switch success case 0 {invalid()}
        }
        require(success);
    }
}
