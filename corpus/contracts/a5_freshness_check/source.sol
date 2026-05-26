// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface IAggregator {
    function latestRoundData() external view returns (
        uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract FreshnessGuarded {
    IAggregator public immutable feed;
    uint256 public constant MAX_AGE = 1 hours;

    constructor(IAggregator _f) { feed = _f; }

    function getPrice() external view returns (uint256) {
        (, int256 answer,, uint256 updatedAt, ) = feed.latestRoundData();
        require(block.timestamp - updatedAt <= MAX_AGE, "stale price");
        require(answer > 0, "bad price");
        return uint256(answer);
    }
}
