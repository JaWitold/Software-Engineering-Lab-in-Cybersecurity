// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./EllipticCurve.sol";

contract SchnorrSignature is EllipticCurve {

    function hash(bytes memory b) public pure returns (uint256) {
        return uint256(keccak256(b)) % GEN_ORDER;
    }

    function verify(uint256[2] memory pubkey, uint256 message, uint256[2] memory X, uint256 s) public view returns (bool)
    {
        G1Point memory pubKeyPoint = G1Point(pubkey[0], pubkey[1]);
        G1Point memory randomPoint = G1Point(X[0], X[1]);

        // h = Hash(X, message)
        uint256 h = hash(abi.encodePacked(X[0], X[1], message));

        // sG = s * G
        G1Point memory sG = mul(G1, s);

        // hA = h * A
        G1Point memory hA = mul(pubKeyPoint, h);

        // X + hA
        G1Point memory XhA = add(randomPoint, hA);

        // Verify that s * G = X + h * A
        return sG.X == XhA.X && sG.Y == XhA.Y;
    }
}
