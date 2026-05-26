// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Wormhole-style archetype: ecrecover fails to 0 which equals an
/// uninitialized guardian slot.
contract WormholeArchetype {
    address[] public guardians;
    constructor(address[] memory g) { guardians = g; }
    function verify(bytes32 h, uint8[] calldata v, bytes32[] calldata r, bytes32[] calldata s) external view returns (bool) {
        for (uint i; i < v.length; ++i) {
            address rec = ecrecover(h, v[i], r[i], s[i]);
            // BUG: malformed signatures recover to 0; if guardians[idx] is unset, also 0.
            if (rec != guardians[i]) return false;
        }
        return true;
    }
}
