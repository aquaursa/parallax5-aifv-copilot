// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.4.24;

/// @notice Solidity 0.4 lacks default checked arithmetic.
contract CompoundLegacy {
    mapping(address => uint256) public balance;
    function mint(uint256 amt) public {
        balance[msg.sender] = balance[msg.sender] + amt;  // overflow possible
    }
    function burn(uint256 amt) public {
        balance[msg.sender] = balance[msg.sender] - amt;  // underflow possible
    }
}
