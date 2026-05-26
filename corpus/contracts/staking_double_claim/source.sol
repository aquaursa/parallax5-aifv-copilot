// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract StakingDoubleClaim {
    mapping(address => uint256) public lastClaimAt;
    mapping(address => uint256) public earned;
    function reward(address user, uint256 amount) external { earned[user] += amount; }
    function claim() external returns (uint256 amt) {
        amt = earned[msg.sender];
        // BUG: doesn't update lastClaimAt; pure-state claim possible repeatedly until earned[u] hits 0
        (bool ok,) = msg.sender.call{value: amt}("");
        require(ok);
        earned[msg.sender] = 0;
        // forgot: lastClaimAt[msg.sender] = block.timestamp;
    }
}
