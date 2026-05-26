// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract FirstWriteOracle {
    mapping(address => uint256) public price;
    function setPrice(address asset, uint256 p) external {
        if (price[asset] == 0) price[asset] = p;  // BUG: first writer wins, no auth
    }
}
