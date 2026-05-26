// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IERC20 { function balanceOf(address) external view returns (uint256); }

contract BeanstalkArchetype {
    IERC20 public immutable govToken;
    mapping(bytes32 => uint256) public votes;
    bytes32 public passedProposal;
    uint256 public immutable supply;
    constructor(IERC20 g, uint256 _supply) { govToken = g; supply = _supply; }

    /// @notice vote with current balance — BUG: flash-loan-attackable
    function vote(bytes32 prop) external {
        uint256 power = govToken.balanceOf(msg.sender);
        votes[prop] += power;
        if (votes[prop] * 2 > supply) passedProposal = prop;
    }
}
