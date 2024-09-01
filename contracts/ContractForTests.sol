// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./Registration.sol";

// Contracts that serves testing purposes
contract ContractForTests is Registration {

    function testAddingEllipticCurve(G1Point memory p1, G1Point memory p2) external view returns (G1Point memory r){
        return add(p1, p2);
    }

    function testMultiplicationEllipticCurve(G1Point memory p, uint256 s) external view returns (G1Point memory r) {
        return multiply(p, s);
    }

    function testVerifySchnorrSignature(uint256 message, uint256[2] memory publicKey, uint256[2] memory R, uint256 s) external view returns (bool) {
        return verifySchnorrSignature(message, publicKey, R, s);
    }

    function testAdddingToArray(
        uint256 message,
        uint256[2] memory newPublicKey,
        uint256[2][] memory Rs,
        uint256[2][] memory RSigmas,
        uint256[] memory sSigmas,
        uint256 sum,
        uint256[2][] memory publicKeys
    ) external {
        addSignature(message, newPublicKey, Rs, RSigmas, sSigmas, sum, publicKeys);
    }

    function testVerifyNodeRingSignature(
        uint256 message,
        uint256[2] memory newPublicKey,
        uint256[2][] memory Rs,
        uint256[2][] memory RSigmas,
        uint256[] memory sSigmas,
        uint256 sum,
        uint256[2][] memory publicKeys
    ) external view returns (bool) {
        return verifyNodeRingSignature(message, newPublicKey, Rs, RSigmas, sSigmas, sum, publicKeys);
    }
}
