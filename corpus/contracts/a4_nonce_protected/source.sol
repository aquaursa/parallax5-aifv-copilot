// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract NoncedAction {
    mapping(address => uint256) public nextNonce;
    function act(uint256 nonce) external {
        require(nonce == nextNonce[msg.sender], "bad nonce");
        nextNonce[msg.sender]++;
    }
}
