// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A1: mints arbitrary shares with no asset backing.
contract MintForFree {
    mapping(address => uint256) public shares;
    uint256 public totalAssets;

    function deposit() external payable {
        totalAssets += msg.value;
        shares[msg.sender] += msg.value;
    }

    /// @dev BUG: lets anyone mint shares without depositing assets.
    function mintFreely(uint256 amount) external {
        shares[msg.sender] += amount;
    }
}
