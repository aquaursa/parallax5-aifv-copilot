// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract DuplicateSigner {
    address[] public validators;
    constructor(address[] memory v) { validators = v; }
    function verify(bytes32 h, uint8[] calldata vs, bytes32[] calldata rs, bytes32[] calldata ss) external view returns (bool) {
        if (vs.length < validators.length / 2 + 1) return false;
        for (uint i; i < vs.length; ++i) {
            address rec = ecrecover(h, vs[i], rs[i], ss[i]);
            // BUG: doesn't check that rec is in validator set or unique
            if (rec == address(0)) return false;
        }
        return true;
    }
}
