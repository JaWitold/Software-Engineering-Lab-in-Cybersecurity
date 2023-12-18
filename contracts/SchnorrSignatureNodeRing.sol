// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./SchnorrSignature.sol";

contract SchnorrSignatureNodeRing is SchnorrSignature {
    // Utility function to compare two G1Point instances
    function isEqual(G1Point memory a, G1Point memory b) internal pure returns (bool) {
        return a.X == b.X && a.Y == b.Y;
    }

    function verify(
        uint256 message,
        uint256[2] memory newPublicKey, // G1
        uint256[2][] memory ephemeralRandomness, // list of G1
        uint256[2][] memory xsigmas, // list of sigmas X's
        uint256[] memory ssigmas, // list of sigmas S's
        uint256 masterSum, // Fr
        uint256[2][] memory publicKeys // list of G1

    ) public view returns (bool) {
        require(ephemeralRandomness.length > 0, "Array ephemeralRandomness is empty");
        require(ephemeralRandomness.length == xsigmas.length, "Arrays ephemeralRandomness and xsigmas are of different lengths");
        require(ephemeralRandomness.length == ssigmas.length, "Arrays ephemeralRandomness and ssigmas are of different lengths");
        require(ephemeralRandomness.length == publicKeys.length, "Arrays ephemeralRandomness and publicKeys are of different lengths");

        G1Point memory sum_t = G1Point(0, 0);
        bool prod = true;
        for (uint i = 0; i < publicKeys.length; i++) {
            // Calculate publicKeysPoints and rsPoints inside the loop
            G1Point memory publicKeyPoint = G1Point(publicKeys[i][0], publicKeys[i][1]);
            G1Point memory rsPoint = G1Point(ephemeralRandomness[i][0], ephemeralRandomness[i][1]);

            // Perform the prod calculation
            prod = prod && verify(newPublicKey, ephemeralRandomness[i][0] + ephemeralRandomness[i][1], xsigmas[i], ssigmas[i]);

            // Calculate the hash
            uint256 h = hash(abi.encodePacked(message, ephemeralRandomness[i][0], ephemeralRandomness[i][1], xsigmas[i][0], xsigmas[i][1], ssigmas[i]));

            // Calculate yH and update sum_t
            if (i == 0) {
                sum_t = add(rsPoint, mul(publicKeyPoint, h));
            } else {
                sum_t = add(sum_t, add(rsPoint, mul(publicKeyPoint, h)));
            }
        }
        return isEqual(mul(G1, masterSum), sum_t) && prod;
    }
}