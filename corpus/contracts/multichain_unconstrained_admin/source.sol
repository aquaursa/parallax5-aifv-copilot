// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IERC20 { function transfer(address,uint256) external returns (bool); }

contract MultichainArchetype {
    address public operator;
    constructor() { operator = msg.sender; }
    /// @notice Operator can sweep any token; rotation is broken.
    function sweep(address token, address to, uint256 amt) external {
        require(msg.sender == operator, "not op");
        IERC20(token).transfer(to, amt);  // no on-chain mandate; off-chain trust
    }
}
