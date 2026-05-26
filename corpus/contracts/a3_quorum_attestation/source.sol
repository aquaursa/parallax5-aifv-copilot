// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract QuorumAction {
    address[] public attestors;
    uint256 public immutable threshold;
    mapping(bytes32 => bool) public executed;

    constructor(address[] memory a, uint256 t) {
        require(t > 0 && t <= a.length, "bad threshold");
        attestors = a;
        threshold = t;
    }

    function act(bytes32 h, uint8[] calldata vs, bytes32[] calldata rs, bytes32[] calldata ss) external {
        require(!executed[h], "replayed");
        require(vs.length >= threshold, "not enough sigs");
        uint256 found;
        for (uint i; i < vs.length; ++i) {
            address rec = ecrecover(h, vs[i], rs[i], ss[i]);
            for (uint j; j < attestors.length; ++j) {
                if (attestors[j] == rec) { found++; break; }
            }
        }
        require(found >= threshold, "insufficient quorum");
        executed[h] = true;
    }
}
