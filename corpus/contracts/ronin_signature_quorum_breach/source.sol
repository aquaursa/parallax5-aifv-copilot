// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract RoninArchetype {
    address[] public validators;
    uint256 public threshold;
    function configure(address[] memory v, uint256 t) external {
        validators = v;
        threshold = t;  // BUG: no check that 2*t > validators.length
    }
}
