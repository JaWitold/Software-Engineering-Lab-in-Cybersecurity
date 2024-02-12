// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./SchnorrSignature.sol";

contract SchnorrSignatureNodeRing is SchnorrSignature {

    // Verifies a node ring Schnorr signature.
    // Parameters:
    // - message: The message that was signed.
    // - newPublicKey: The public key for the signature, represented as an array of two uint256 values (X, Y) that form an elliptic curve point.
    // - Rs: Array of R values from each signer's Schnorr signature, where each R value is an elliptic curve point represented as an array of two uint256 values (X, Y).
    // - RSigmas: Array of elliptic curve points representing the R part of each signer's signature, where each point is an array of two uint256 values (X, Y).
    // - sSigmas: Array of scalar S values from each signer's Schnorr signature, representing the S part of the signatures.
    // - sum: The aggregated scalar value obtained from the ring signature process.
    // - publicKeys: Array of public keys from the ring of signers, where each key is an elliptic curve point represented as an array of two uint256 values (X, Y).
    // Returns true if the ring signature is valid, false otherwise.
    function verifyNodeRingSignature(
        uint256 message,
        uint256[2] memory newPublicKey,
        uint256[2][] memory Rs,
        uint256[2][] memory RSigmas,
        uint256[] memory sSigmas,
        uint256 sum,
        uint256[2][] memory publicKeys
    ) public view returns (bool) {
        // Validation of input arrays to ensure they are of expected lengths.
        require(publicKeys.length > 0, "No public keys provided");
        require(publicKeys.length == RSigmas.length, "Mismatch in RSigmas and public keys count");
        require(publicKeys.length == sSigmas.length, "Mismatch in sSigmas and public keys count");
        require(publicKeys.length == Rs.length, "Mismatch in Rs and public keys count");

        // Initialize a point on the curve to aggregate sums.
        G1Point memory aggregatePoint = G1Point(0, 0);
        // Flag to verify each sub-signature within the ring.
        bool subSignatureVerified = true;

        // Iterate through each public key to verify its sub-signature and aggregate.
        for (uint i = 0; i < publicKeys.length; i++) {
            // Verifies each sub-signature by checking if the given sSigma generates the expected RSigma when combined with the message and public key.
            // This ensures that each signer's part of the signature is valid.
            subSignatureVerified = subSignatureVerified && verifySignature(Rs[i][0] + Rs[i][1], newPublicKey, RSigmas[i], sSigmas[i]);

            // Compute hash of the message combined with the R and RSigma values, and the sSigma for this iteration.
            // This hash represents a unique challenge for each signer's contribution.
            uint256 h = hash(abi.encodePacked(message, Rs[i][0], Rs[i][1], RSigmas[i][0], RSigmas[i][1], sSigmas[i]));

            // Aggregate the sum of all R points and public key points weighted by the hash.
            // This is part of the verification equation for the ring signature.
            aggregatePoint = add(aggregatePoint, add(G1Point(Rs[i][0], Rs[i][1]), multiply(G1Point(publicKeys[i][0], publicKeys[i][1]), h)));
        }

        // Verify the final aggregated signature:
        // Check if multiplying the generator point by the aggregated scalar sum yields the same point as the aggregated sum of R and weighted public keys.
        // Also, ensure that all sub-signatures were verified successfully.
        return isEqual(multiply(G1, sum), aggregatePoint) && subSignatureVerified;
    }
}
