// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A4: action can be called arbitrarily many times.
contract ReplayableAction {
    uint256 public counter;
    function act() external { counter++; }  // can be called repeatedly; no temporal binding
}
