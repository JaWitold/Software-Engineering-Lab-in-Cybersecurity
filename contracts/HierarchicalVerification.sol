// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./SignatureStorage.sol";

contract HierarchicalVerification is SignatureStorage {
    // Verifies a hierarchical node ring signature.
    // Parameters:
    // - message: The original message that was signed.
    // - newPublicKey: The newly generated public key for this level of the hierarchy.
    // - Rs: An array of R values, each being a part of individual Schnorr signatures collected in the ring signature.
    // - RSigmas: The R components of the aggregated signatures for verification.
    // - sSigmas: The S components of the aggregated signatures, representing commitment scalars.
    // - sum: The aggregated sum of scalars, used to verify the combined signature's validity.
    // - publicKeys: The public keys of all participants in the ring signature.
    // Returns true if the signature is valid across the hierarchical structure, false otherwise.
    function verifyHierarchicalSignature(
        uint256 message,
        uint256[2] memory newPublicKey,
        uint256[2][] memory Rs,
        uint256[2][] memory RSigmas,
        uint256[] memory sSigmas,
        uint256 sum,
        uint256[2][] memory publicKeys
    ) public view returns (bool) {
        // Verification step to ensure the integrity and authenticity of the provided signature.
        require(verifyNodeRingSignature(message, newPublicKey, Rs, RSigmas, sSigmas, sum, publicKeys), "Invalid signature");

        // Iterates through all provided public keys to verify each corresponding signature in the hierarchical structure.
        for (uint256 i = 0; i < publicKeys.length; i++) {
            // Retrieve signatures associated with the current public key, indicating a hierarchical relationship.
            Signature[] memory signatures = getSignaturesByNewPublicKey(publicKeys[i]);

            // If no signatures are found, we're at a leaf node of the hierarchy, and no further action is needed.
            if (signatures.length == 0) {
                return true;
            }

            // For internal nodes in the hierarchy, recursively verify each signature.
            // This step ensures that each level of the hierarchy is authenticated.
            for (uint256 j = 0; j < signatures.length; j++) {
                Signature memory s = signatures[j];
                verifyHierarchicalSignature(s.message, s.newPublicKey, s.Rs, s.RSigmas, s.sSigmas, s.sum, s.publicKeys);
            }
        }
        // Returns true if all signatures in the hierarchy are valid, ensuring the integrity of the entire structure.
        return true;
    }
}
