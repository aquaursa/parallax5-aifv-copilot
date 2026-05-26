// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract OracleGovAttack {
    address public owner;
    address public oracleAddr;
    constructor() { owner = msg.sender; }
    function setOracle(address a) external {
        require(msg.sender == owner, "not owner");
        // BUG: no timelock; owner can flip oracle to attacker contract instantly
        oracleAddr = a;
    }
}
