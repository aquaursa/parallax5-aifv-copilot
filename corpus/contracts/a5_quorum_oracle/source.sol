// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface IFeed { function latestAnswer() external view returns (int256); function lastUpdate() external view returns (uint256); }

contract MedianOracle {
    IFeed[] public feeds;
    uint256 public constant MAX_AGE = 1 hours;
    constructor(IFeed[] memory _f) { feeds = _f; }

    function getPrice() external view returns (uint256) {
        uint256 fresh;
        for (uint i; i < feeds.length; ++i) {
            if (block.timestamp - feeds[i].lastUpdate() <= MAX_AGE) fresh++;
        }
        require(fresh >= (feeds.length / 2) + 1, "quorum failed");
        return uint256(feeds[0].latestAnswer());  // simplified — full median omitted
    }
}
