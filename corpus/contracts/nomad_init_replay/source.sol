// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Nomad-style archetype: a one-time init was set up
/// such that any message with a zero root is treated as valid.
contract NomadArchetype {
    mapping(bytes32 => bool) public acceptable;
    function init(bytes32 root) external { acceptable[root] = true; }
    function process(bytes32 msgRoot, bytes calldata) external view {
        require(acceptable[msgRoot], "not accepted");
        // BUG: if root == 0x0 is registered as acceptable (by accident or attack),
        // every message verifies because Merkle proof of empty also yields 0.
    }
}
