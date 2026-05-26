// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract MerkleDrop {
    bytes32 public root;
    mapping(address => bool) public claimed;
    function claim(uint256 amt, bytes32[] calldata proof) external {
        require(!claimed[msg.sender], "claimed");
        // BUG: doesn't actually verify proof; only checks proof.length > 0
        require(proof.length > 0, "no proof");
        claimed[msg.sender] = true;
        payable(msg.sender).transfer(amt);
    }
}
