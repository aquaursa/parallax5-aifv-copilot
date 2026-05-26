// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract VirtualOffsetVault {
    uint256 constant V_SHARES = 10**6;
    uint256 constant V_ASSETS = 1;
    uint256 public totalShares;
    uint256 public totalAssets;
    mapping(address => uint256) public shares;

    function deposit(uint256 amt) external {
        uint256 minted = (amt * (totalShares + V_SHARES)) / (totalAssets + V_ASSETS);
        require(minted > 0, "zero shares");
        shares[msg.sender] += minted;
        totalShares += minted;
        totalAssets += amt;
    }
}
