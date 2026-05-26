// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IPriceOracle { function priceOf(address) external view returns (uint256); }

contract DForceArchetype {
    IPriceOracle public oracle;
    mapping(address => uint256) public price;
    constructor(IPriceOracle o) { oracle = o; }
    function refresh(address asset) external {
        // BUG: re-pulls from oracle that itself sources from this contract
        price[asset] = oracle.priceOf(asset);
    }
}
