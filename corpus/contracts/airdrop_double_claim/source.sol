// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract Airdrop {
    mapping(address => uint256) public eligible;
    mapping(address => bool) public claimed;
    function claim() external {
        require(eligible[msg.sender] > 0, "none");
        (bool ok,) = msg.sender.call{value: eligible[msg.sender]}("");
        require(ok);
        claimed[msg.sender] = true;  // BUG: external call before state update; reentry can drain
    }
}
