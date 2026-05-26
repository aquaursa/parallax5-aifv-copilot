// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract StakingInflation {
    uint256 public totalShares;
    uint256 public totalAssets;
    receive() external payable { totalAssets += msg.value; }  // BUG: direct donation accepted
    function stake() external payable returns (uint256 shares) {
        shares = totalShares == 0 ? msg.value : (msg.value * totalShares) / totalAssets;
        require(shares > 0, "zero");
        totalShares += shares;
        totalAssets += msg.value;
    }
}
