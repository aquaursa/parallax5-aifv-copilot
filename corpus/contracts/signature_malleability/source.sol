// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract Malleable {
    function recover(bytes32 h, uint8 v, bytes32 r, bytes32 s) external pure returns (address) {
        // BUG: no `s` low-half-order check; both (v,r,s) and (v^1,r,n-s) recover same signer
        return ecrecover(h, v, r, s);
    }
}
