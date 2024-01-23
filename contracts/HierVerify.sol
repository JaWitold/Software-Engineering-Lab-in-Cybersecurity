// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./SignaturesStorage.sol";

contract HierVerify is SignaturesStorage {

function hierVerify(
        uint256 message,
        uint256[2] memory newPublicKey, // G1
        uint256[2][] memory ephemeralRandomness, // list of G1
        uint256[2][] memory xsigmas, // list of sigmas X's
        uint256[] memory ssigmas, // list of sigmas S's
        uint256 masterSum, // Fr
        uint256[2][] memory publicKeys // list of G1
    ) public view returns (bool) {
         require(
            schnorrNrVerify(
                message,
                newPublicKey,
                ephemeralRandomness,
                xsigmas,
                ssigmas,
                masterSum,
                publicKeys
            ) == true,
            "Signature isn't valid"
        );

        for (uint256 i = 0; i < publicKeys.length; i++) {
            uint256[2] memory y = publicKeys[i];
            Signature[] memory signatures = getSignaturesByNewPublicKey(y);
            if (signatures.length == 0) {
                // leaf
                return true;
            }

            for (uint256 j = 0; j < signatures.length; j++) {
                Signature memory s = signatures[j];
                hierVerify(s.message, s.newPublicKey, s.ephemeralRandomness, s.xsigmas, s.ssigmas, s.masterSum, s.publicKeys);
            }
        }
        return true;
    }

    function getSignaturesByNewPublicKey(uint256[2] memory targetPublicKey) public view returns (Signature[] memory) {
        uint256[] memory indices = signaturesByNewPublicKey[
            abi.encodePacked(targetPublicKey[0], targetPublicKey[1])
        ];
        Signature[] memory result = new Signature[](indices.length);

        for (uint256 i = 0; i < indices.length; i++) {
            result[i] = signatures[indices[i]];
        }

        return result;
    }
}
