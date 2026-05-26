// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract NoDeadlinePermit {
    mapping(address => uint256) public nonces;
    bytes32 public DOMAIN_SEPARATOR;
    function permit(address owner, address spender, uint256 value, /*uint256 deadline,*/ uint8 v, bytes32 r, bytes32 s) external {
        // BUG: no deadline enforced; ancient signatures still valid
        bytes32 struct_ = keccak256(abi.encode(owner, spender, value, nonces[owner]++));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, struct_));
        require(ecrecover(digest, v, r, s) == owner);
    }
}
