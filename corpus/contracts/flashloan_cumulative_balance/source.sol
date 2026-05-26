// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IERC20 { function balanceOf(address) external view returns (uint256); }
contract CumulativePrice {
    IERC20 public token;
    function setToken(IERC20 t) external { token = t; }
    function tvl() external view returns (uint256) {
        return token.balanceOf(address(this));  // BUG: trivially inflated by flashloan transfer
    }
}
