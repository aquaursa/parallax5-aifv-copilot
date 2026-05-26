// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IPool { function getReserves() external view returns (uint256, uint256); }

contract HundredArchetype {
    IPool public pool;
    bool internal entered;
    function setPool(IPool p) external { pool = p; }
    function getPrice() external view returns (uint256) {
        (uint256 a, uint256 b) = pool.getReserves();  // mid-callback read returns stale ratio
        return (a * 1e18) / b;
    }
}
