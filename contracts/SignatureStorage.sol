// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./NodeRingSchnorrSignature.sol";

// A contract that stores and verifies Schnorr node ring signatures.
// It extends NodeRingSchnorrSignature to utilize its node ring signature verification capabilities.
contract SignatureStorage is NodeRingSchnorrSignature {
    // Defines a signature structure to hold all components of a node ring Schnorr signature.
    struct Signature {
        uint256 message;            // The message that was signed.
        uint256[2] newPublicKey;    // The public key for the signature, represented as an array of two uint256 values (X, Y) that form an elliptic curve point.
        uint256[2][] Rs;            // Array of R values from each signer's signature, where each R value is an elliptic curve point represented as an array of two uint256 values (X, Y).
        uint256[2][] RSigmas;       // Array of elliptic curve points representing the R part of each signer's signature, where each point is an array of two uint256 values (X, Y).
        uint256[] sSigmas;          // Array of scalar S values from each signer's signature, representing the S part of the signatures.
        uint256 sum;                // The aggregated scalar value from the ring signature process.
        uint256[2][] publicKeys;    // Array of public keys from the ring of signers, where each key is an elliptic curve point represented as an array of two uint256 values (X, Y).
    }

    // Stores all signatures collected by the contract.
    Signature[] public storedSignatures;

    // Mapping to associate public keys with indices of signatures in which they are used.
    mapping(uint256 => mapping(uint256 => uint256[])) public signatureIndicesByPublicKey;

    // Mapping to associate new public keys with indices of signatures where they serve as the combined public key.
    mapping(uint256 => mapping(uint256 => uint256[])) public signatureIndicesByNewPublicKey;

    // Stores a new signature after verification.
    // Validates the signature using `verifyNodeRingSignature` before storage.
    // Indexes the signature by each involved public key and the new public key.
    // Parameters:
    // - message: The message that was signed.
    // - newPublicKey: The public key for the signature, represented as an array of two uint256 values (X, Y) that form an elliptic curve point.
    // - Rs: Array of R values from each signer's Schnorr signature, where each R value is an elliptic curve point represented as an array of two uint256 values (X, Y).
    // - RSigmas: Array of elliptic curve points representing the R part of each signer's signature, where each point is an array of two uint256 values (X, Y).
    // - sSigmas: Array of scalar S values from each signer's Schnorr signature, representing the S part of the signatures.
    // - sum: The aggregated scalar value obtained from the ring signature process.
    // - publicKeys: Array of public keys from the ring of signers, where each key is an elliptic curve point represented as an array of two uint256 values (X, Y).
    function addSignature(
        uint256 message,
        uint256[2] memory newPublicKey,
        uint256[2][] memory Rs,
        uint256[2][] memory RSigmas,
        uint256[] memory sSigmas,
        uint256 sum,
        uint256[2][] memory publicKeys
    ) internal {
        // Verification step to ensure the integrity and authenticity of the provided signature.
        require(verifyNodeRingSignature(message, newPublicKey, Rs, RSigmas, sSigmas, sum, publicKeys), "Invalid signature");

        // Constructing a new signature record.
        Signature memory signature = Signature(message, newPublicKey, Rs, RSigmas, sSigmas, sum, publicKeys);

        // Storing the signature and keeping track of its index.
        uint256 signatureIndex = storedSignatures.length;
        storedSignatures.push(signature);

        // Indexing the signature by each public key.
        for (uint256 i = 0; i < publicKeys.length; i++) {
            signatureIndicesByPublicKey[publicKeys[i][0]][publicKeys[i][1]].push(signatureIndex);
        }

        // Indexing the signature by the new public key.
        signatureIndicesByNewPublicKey[newPublicKey[0]][newPublicKey[1]].push(signatureIndex);
    }

    // Retrieves signature under index idx
    function getSignatureByIdx(uint256 idx) public view returns (Signature memory) {
        require(idx < storedSignatures.length, "Index exceeds number of signatures stored");
        return storedSignatures[idx];
    }

    // Retrieves signatures associated with a specific public key.
    // Utilizes `extractSignatures` to return an array of Signature structs.
    function getSignaturesByPublicKey(uint256[2] memory publicKey) public view returns (Signature[] memory) {
        return extractSignatures(signatureIndicesByPublicKey[publicKey[0]][publicKey[1]]);
    }

    // Retrieves signatures associated with a specific new public key.
    // Utilizes `extractSignatures` to return an array of Signature structs.
    function getSignaturesByNewPublicKey(uint256[2] memory publicKey) public view returns (Signature[] memory) {
        return extractSignatures(signatureIndicesByNewPublicKey[publicKey[0]][publicKey[1]]);
    }

    // Internal helper function to construct an array of Signature structs from an array of indices.
    // This allows for efficient retrieval of signature data stored in the contract.
    function extractSignatures(uint256[] memory indices) private view returns (Signature[] memory) {
        Signature[] memory signatures = new Signature[](indices.length);
        for (uint256 i = 0; i < indices.length; i++) {
            signatures[i] = storedSignatures[indices[i]];
        }
        return signatures;
    }
}
