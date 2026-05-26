// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IOracle { function price(address) external view returns (uint256); }
contract LiquidationVuln {
    IOracle public oracle;
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;
    function liquidate(address user) external {
        uint256 cVal = collateral[user] * oracle.price(user);
        require(cVal < debt[user] * 80 / 100, "healthy");  // BUG: no staleness check
        // ... seize collateral
    }
}
