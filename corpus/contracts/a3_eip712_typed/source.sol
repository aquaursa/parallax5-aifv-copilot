// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract EIP712Action {
    bytes32 public immutable DOMAIN_SEPARATOR;
    address public immutable signer;
    mapping(bytes32 => bool) public used;

    constructor(address _signer, uint256 chainId) {
        signer = _signer;
        DOMAIN_SEPARATOR = keccak256(abi.encode(
            keccak256("EIP712Domain(uint256 chainId)"),
            chainId
        ));
    }

    function act(uint256 nonce, uint8 v, bytes32 r, bytes32 s) external {
        bytes32 structHash = keccak256(abi.encode(keccak256("Action(uint256 nonce)"), nonce));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
        require(!used[digest], "replayed");
        address rec = ecrecover(digest, v, r, s);
        require(rec == signer && rec != address(0), "bad sig");
        used[digest] = true;
    }
}
