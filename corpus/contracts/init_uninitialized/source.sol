// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract Uninitialized {
    address public admin;
    // BUG: no constructor/initializer; first caller becomes admin
    function init() external {
        require(admin == address(0), "init");
        admin = msg.sender;
    }
}
