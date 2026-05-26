// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract RoleAccess {
    mapping(bytes32 => mapping(address => bool)) public has;
    bytes32 public constant ADMIN = keccak256("ADMIN");
    bytes32 public constant PAUSER = keccak256("PAUSER");

    bool public paused;
    uint256 public fee;

    constructor() { has[ADMIN][msg.sender] = true; }

    function grant(bytes32 r, address to) external {
        require(has[ADMIN][msg.sender], "not admin");
        has[r][to] = true;
    }
    function setFee(uint256 f) external {
        require(has[ADMIN][msg.sender], "not admin");
        fee = f;
    }
    function pause() external {
        require(has[PAUSER][msg.sender], "not pauser");
        paused = true;
    }
}
