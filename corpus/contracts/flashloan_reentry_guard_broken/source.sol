// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract BrokenGuard {
    mapping(bytes4 => bool) internal locked;
    modifier nonReentrant() {
        require(!locked[msg.sig], "locked");
        locked[msg.sig] = true;
        _;
        locked[msg.sig] = false;
    }
    /// @notice BUG: separate locks per selector; cross-function reentrancy possible.
    function f() external nonReentrant {}
    function g() external nonReentrant {}
}
