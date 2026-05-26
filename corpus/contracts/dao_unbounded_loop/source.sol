// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract UnboundedLoopArchetype {
    address[] public members;
    function join() external { members.push(msg.sender); }
    function payAll(uint256 perMember) external payable {
        for (uint i; i < members.length; ++i) {  // O(n) — can hit block gas limit
            payable(members[i]).transfer(perMember);
        }
    }
}
