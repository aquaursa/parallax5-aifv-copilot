// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract BadAllowance {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    function transferFrom(address from, address to, uint256 amt) external {
        // BUG: no allowance check; anyone can move anyone's tokens
        balanceOf[from] -= amt;
        balanceOf[to] += amt;
    }
}
