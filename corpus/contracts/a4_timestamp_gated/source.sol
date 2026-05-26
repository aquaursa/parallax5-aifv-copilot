// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract Timelock {
    uint256 public immutable unlockAt;
    address public immutable beneficiary;

    constructor(uint256 _unlockAt, address _b) {
        require(_unlockAt > block.timestamp, "past time");
        unlockAt = _unlockAt;
        beneficiary = _b;
    }

    function withdraw() external {
        require(block.timestamp >= unlockAt, "still locked");
        require(msg.sender == beneficiary, "not beneficiary");
        (bool ok,) = beneficiary.call{value: address(this).balance}("");
        require(ok, "send failed");
    }

    receive() external payable {}
}
