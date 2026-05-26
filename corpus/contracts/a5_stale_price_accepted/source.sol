// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface IFeed { function latestAnswer() external view returns (int256); }

/// @notice Violates A5: accepts arbitrarily stale oracle responses.
contract NoFreshnessCheck {
    IFeed public immutable feed;
    constructor(IFeed _f) { feed = _f; }
    function getPrice() external view returns (uint256) {
        int256 a = feed.latestAnswer();
        return a > 0 ? uint256(a) : 0;
    }
}
