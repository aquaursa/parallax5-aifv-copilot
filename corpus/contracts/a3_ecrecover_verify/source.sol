// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract SignedAction {
    address public immutable signer;
    mapping(bytes32 => bool) public used;
    constructor(address _signer) { signer = _signer; }

    function act(bytes32 msgHash, uint8 v, bytes32 r, bytes32 s) external {
        require(!used[msgHash], "replayed");
        address rec = ecrecover(msgHash, v, r, s);
        require(rec == signer, "bad sig");
        used[msgHash] = true;
    }
}
