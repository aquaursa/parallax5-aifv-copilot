// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A3: message signed for chain A can be replayed on chain B.
contract NoChainBinding {
    address public immutable signer;
    constructor(address _s) { signer = _s; }

    function act(bytes32 messageHash, uint8 v, bytes32 r, bytes32 s) external view returns (bool) {
        // messageHash doesn't include chain id; same signature works everywhere
        return ecrecover(messageHash, v, r, s) == signer;
    }
}
