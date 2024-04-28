// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./EllipticCurve.sol";

contract SchnorrSignature is EllipticCurve {

    // Hash function used in the Schnorr signature scheme.
    // It takes a byte array as input and returns a hash value modulo the generator order.
    function hash(bytes memory b) internal pure returns (uint256) {
        return uint256(keccak256(b)) % GEN_ORDER;
    }

    // Verifies a Schnorr signature.
    // Parameters:
    // - publicKey: The message (as a uint256) that was signed.
    // - pubkey: Public key as an array of two uint256 representing an elliptic curve point (X, Y).
    // - R: value of the signature (elliptic curve point).
    // - s: value of the signature (scalar).
    // Returns true if the signature is valid, false otherwise.
    function verifySignature(uint256 message, uint256[2] memory publicKey, uint256[2] memory R, uint256 s) internal view returns (bool) {
        // Calculate the hash of the concatenation of X, Y of the R value and the message.
        // This represents the challenge in the Schnorr signature scheme.
        uint256 h = hash(abi.encode(R[0], R[1], message));

        // Compute X + h * A, where A is the public key.
        // This is the other part of the verification equation in Schnorr's signature.
        G1Point memory XhA = add(G1Point(R[0], R[1]), multiply(G1Point(publicKey[0], publicKey[1]), h));

        // Compute s * G, where G is the generator point of the elliptic curve.
        // Verify the Schnorr signature by checking the equality of s * G and X + h * A.
        // If they are equal, the signature is valid.
        return isEqual(multiply(G1, s), XhA);
    }

    // function only for testing
    function testVerifySignature(uint256 message, uint256[2] memory publicKey, uint256[2] memory R, uint256 s) public view returns (bool) {
        return verifySignature(message, publicKey, R, s);
    }
}
