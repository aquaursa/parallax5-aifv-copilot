// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract OwnerSetter {
    address public immutable owner;
    uint256 public value;

    constructor() { owner = msg.sender; }

    function setValue(uint256 v) external {
        require(msg.sender == owner, "not owner");
        value = v;
    }
}
