// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./HierarchicalVerification.sol";

contract Registration is HierarchicalVerification {
    mapping(uint256 => mapping(uint256 => bool)) storedPublicKey;

    // Parameters:
    // - publicKey: The message (as a uint256) that was signed.
    // - pubkey: Public key as an array of two uint256 representing an elliptic curve point (X, Y).
    // - R: value of the signature (elliptic curve point).
    // - s: value of the signature (scalar).
    // Returns true if the signature is valid, false otherwise.
    function registerKey(uint256[2] memory publicKey, uint256[2] memory R, uint256 s) external returns (bool) {
        require(verifySchnorrSignature(publicKey[0], publicKey, R, s));
        storedPublicKey[publicKey[0]][publicKey[1]] = true;
        return true;
    }

    function getStoredPublicKey(uint256[2] memory publicKey) public view returns(bool){
        return storedPublicKey[publicKey[0]][publicKey[1]];
    }

    function addSignatureAndRegister(
        uint256 message,
        uint256[2] memory newPublicKey,
        uint256[2][] memory Rs,
        uint256[2][] memory RSigmas,
        uint256[] memory sSigmas,
        uint256 sum,
        uint256[2][] memory publicKeys
    ) public {
        for (uint256 i = 0; i < publicKeys.length; i++) {
            require(getStoredPublicKey(publicKeys[i]), "Public Key not registered");
        }
        addSignature(message, newPublicKey, Rs, RSigmas, sSigmas, sum, publicKeys);
        storedPublicKey[newPublicKey[0]][newPublicKey[1]] = true;
    }
}
