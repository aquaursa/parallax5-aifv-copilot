// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IDex { function spotPrice() external view returns (uint256); }

contract MangoArchetype {
    IDex public immutable dex;
    constructor(IDex d) { dex = d; }
    function getCollateralValue() external view returns (uint256) {
        return dex.spotPrice();  // BUG: spot price manipulable by single tx
    }
}
