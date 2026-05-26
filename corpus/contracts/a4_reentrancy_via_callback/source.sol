// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A4: state update after external call enables reentrancy
/// (a temporal-distinctness violation in PARALLAX-5 framing).
contract ReentrancyVuln {
    mapping(address => uint256) public balance;

    function deposit() external payable { balance[msg.sender] += msg.value; }

    function withdraw(uint256 amt) external {
        require(balance[msg.sender] >= amt, "insufficient");
        (bool ok,) = msg.sender.call{value: amt}("");  // external call first
        require(ok, "send failed");
        balance[msg.sender] -= amt;  // state update second — BUG
    }
}
