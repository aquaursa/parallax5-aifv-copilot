// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract TwoStepOwnable {
    address public owner;
    address public pendingOwner;

    constructor() { owner = msg.sender; }

    function transfer(address newOwner) external {
        require(msg.sender == owner, "not owner");
        pendingOwner = newOwner;
    }
    function accept() external {
        require(msg.sender == pendingOwner, "not pending");
        owner = pendingOwner;
        delete pendingOwner;
    }
}
