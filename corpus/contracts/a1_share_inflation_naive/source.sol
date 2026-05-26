// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract NaiveVault {
    uint256 public totalShares;
    uint256 public totalAssets;
    mapping(address => uint256) public shares;

    function deposit(uint256 amt) external {
        uint256 minted;
        if (totalShares == 0) {
            minted = amt;
        } else {
            minted = (amt * totalShares) / totalAssets;  // can round to 0
        }
        shares[msg.sender] += minted;
        totalShares += minted;
        totalAssets += amt;
    }
}
