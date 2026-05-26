// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract CEISafe {
    mapping(address => uint256) public balance;
    function deposit() external payable { balance[msg.sender] += msg.value; }
    function withdraw(uint256 amt) external {
        require(balance[msg.sender] >= amt, "insufficient");
        balance[msg.sender] -= amt;          // effect
        (bool ok,) = msg.sender.call{value: amt}("");  // interaction
        require(ok, "send failed");
    }
}
