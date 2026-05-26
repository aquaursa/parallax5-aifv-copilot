// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Trivially A1-safe: balance never changes after deployment.
contract ConstantBalance {
    uint256 public immutable balance;

    constructor(uint256 _balance) {
        balance = _balance;
    }

    function getBalance() external view returns (uint256) {
        return balance;
    }
}
