// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract PartialUpdate {
    mapping(address => uint256) public balance;
    uint256 public totalSupply;  // never decremented
    function deposit() external payable {
        balance[msg.sender] += msg.value;
        totalSupply += msg.value;
    }
    function withdraw(uint256 amt) external {
        balance[msg.sender] -= amt;  // BUG: totalSupply not updated
        payable(msg.sender).transfer(amt);
    }
}
