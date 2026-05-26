// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice One asset, one share, 1:1 accounting. Always A1.
contract OneToOnePool {
    mapping(address => uint256) public balanceOf;
    uint256 public totalBalance;

    function deposit() external payable {
        balanceOf[msg.sender] += msg.value;
        totalBalance += msg.value;
    }

    function withdraw(uint256 amt) external {
        require(balanceOf[msg.sender] >= amt, "insufficient");
        balanceOf[msg.sender] -= amt;
        totalBalance -= amt;
        (bool ok,) = msg.sender.call{value: amt}("");
        require(ok, "send failed");
    }
}
