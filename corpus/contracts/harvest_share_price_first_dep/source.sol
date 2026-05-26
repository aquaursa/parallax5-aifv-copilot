// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract HarvestArchetype {
    uint256 public totalSupply;
    uint256 public totalAssets;
    function deposit(uint256 amt) external returns (uint256 shares) {
        if (totalSupply == 0) {
            shares = amt;  // first depositor sets price = 1
        } else {
            shares = (amt * totalSupply) / totalAssets;
        }
        totalSupply += shares;
        totalAssets += amt;
    }
}
