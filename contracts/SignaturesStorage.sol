// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./SchnorrSignatureNodeRing.sol";

contract SignaturesStorage {
    SchnorrSignatureNodeRing schnorrSigNr;

    constructor(address externalContractAddress) {
        schnorrSigNr = SchnorrSignatureNodeRing(externalContractAddress);
    }

    struct Signature {
        uint256 message;
        uint256[2] newPublicKey;
        uint256[2][] ephemeralRandomness;
        uint256[2][] xsigmas;
        uint256[] ssigmas;
        uint256 masterSum;
        uint256[2][] publicKeys;
    }

    Signature[] public signatures;

    // Nested mapping becasue key consists of two uint256
    // mapping(uint256 => mapping(uint256 => uint256[]))
    //     public signaturesByPublicKey;
    // or the following?
    mapping(bytes => uint256[]) public signaturesByPublicKey;

    // Function to store a new signature
    function storeSignature(
        uint256 _message,
        uint256[2] memory _newPublicKey,
        uint256[2][] memory _ephemeralRandomness,
        uint256[2][] memory _xsigmas,
        uint256[] memory _ssigmas,
        uint256 _masterSum,
        uint256[2][] memory _publicKeys
    ) public {
        require(
            schnorrSigNr.verify(
                _message,
                _newPublicKey,
                _ephemeralRandomness,
                _xsigmas,
                _ssigmas,
                _masterSum,
                _publicKeys
            ) == true,
            "Signature isn't valid"
        );

        Signature memory newSignature = Signature({
            message: _message,
            newPublicKey: _newPublicKey,
            ephemeralRandomness: _ephemeralRandomness,
            xsigmas: _xsigmas,
            ssigmas: _ssigmas,
            masterSum: _masterSum,
            publicKeys: _publicKeys
        });

        uint256 index = signatures.length;
        signatures.push(newSignature);

        for (uint256 i = 0; i < _publicKeys.length; i++) {
            signaturesByPublicKey[
                abi.encodePacked(_publicKeys[i][0], _publicKeys[i][1])
            ].push(index);
        }
        signaturesByPublicKey[
            abi.encodePacked(_newPublicKey[0], _newPublicKey[1])
        ].push(index);
    }

    // Function to retrieve all signatures for a specified public key
    function getSignaturesForPublicKey(
        uint256[2] memory targetPublicKey
    ) public view returns (Signature[] memory) {
        uint256[] memory indices = signaturesByPublicKey[
            abi.encodePacked(targetPublicKey[0], targetPublicKey[1])
        ];
        Signature[] memory result = new Signature[](indices.length);

        for (uint256 i = 0; i < indices.length; i++) {
            result[i] = signatures[indices[i]];
        }

        return result;
    }

    // Function to get the count of stored signatures
    function getSignatureCount() public view returns (uint256) {
        return signatures.length;
    }

    // Function to get details of a specific signature
    function getSignatureDetails(
        uint256 index
    ) public view returns (Signature memory) {
        require(index < signatures.length, "Index out of bounds");
        return signatures[index];
    }
}
