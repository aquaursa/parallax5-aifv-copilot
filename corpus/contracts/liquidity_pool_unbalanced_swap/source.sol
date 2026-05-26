// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract NoSlippageAMM {
    uint256 public reserve0;
    uint256 public reserve1;
    function swap(uint256 amt0In) external returns (uint256 amt1Out) {
        // BUG: no min-out param; sandwichable
        amt1Out = (amt0In * reserve1) / (reserve0 + amt0In);
        reserve0 += amt0In;
        reserve1 -= amt1Out;
    }
}
