// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A2: anyone can change a critical parameter.
contract UnprotectedSetter {
    uint256 public criticalThreshold;
    function setThreshold(uint256 v) external { criticalThreshold = v; }
}
