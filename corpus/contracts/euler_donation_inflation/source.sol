// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract EulerArchetype {
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;

    function donate() external payable { collateral[msg.sender] += msg.value; }
    function borrow(uint256 amt) external {
        require(amt <= collateral[msg.sender] * 2, "undercollat");  // composite path
        debt[msg.sender] += amt;
        (bool ok,) = msg.sender.call{value: amt}("");
        require(ok, "send");
    }
}
