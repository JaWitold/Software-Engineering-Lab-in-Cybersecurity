// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./SchnorrSignature.sol";

contract NrVerify is SchnorrSignature {
    // Utility function to compare two G1Point instances
    function isEqual(G1Point memory a, G1Point memory b) internal pure returns (bool) {
        return a.X == b.X && a.Y == b.Y;
    }

    function verify(
        uint256 message,
        uint256[2] memory masterPublicKey, // G1
        uint256[2] memory aSign, // G1
        uint256[2][] memory rs_, // list of G1
        uint256[2][] memory sigmas, // list of pairs of Fr
        uint256 s_, // Fr
        uint256[2][] memory publicKeys // list of G1
    ) public view returns (bool) {
        require(rs_.length > 0, "Array rs_ is empty");
        require(rs_.length == sigmas.length, "Arrays rs_ and sigmas are of different lengths");
        require(rs_.length == publicKeys.length, "Arrays rs_ and publicKeys are of different lengths");

        G1Point memory sum_t = G1;
        bool prod = true;

        for (uint i = 0; i < publicKeys.length; i++) {
            // Calculate publicKeysPoints and rsPoints inside the loop
            G1Point memory publicKeyPoint = G1Point(publicKeys[i][0], publicKeys[i][1]);
            G1Point memory rsPoint = G1Point(rs_[i][0], rs_[i][1]);

            // Perform the prod calculation
            prod = prod && verify(masterPublicKey, message, sigmas[i], s_);

            // Calculate the hash
            uint256 h = hash(abi.encodePacked(message, rs_[i][0], rs_[i][1], sigmas[i][0], sigmas[i][1]));

            // Calculate yH and update sum_t
            G1Point memory yH = mul(publicKeyPoint, h);
            sum_t = add(sum_t, add(rsPoint, yH));
        }

        return isEqual(mul(G1, s_), sum_t) && prod;
    }
}