// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A3: doesn't check ecrecover failure (returns address(0)).
contract WeakSignerCheck {
    function act(bytes32 h, uint8 v, bytes32 r, bytes32 s, address claimed) external pure returns (bool) {
        address rec = ecrecover(h, v, r, s);
        return rec == claimed;  // BUG: if both fail to 0, accepts
    }
}
