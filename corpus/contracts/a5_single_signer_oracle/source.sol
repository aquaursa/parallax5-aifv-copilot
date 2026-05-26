// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A5: any party can push price with no oracle attestation.
contract OpenOracle {
    mapping(address => uint256) public price;
    function setPrice(address asset, uint256 v) external { price[asset] = v; }
}
