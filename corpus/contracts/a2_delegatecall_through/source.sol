// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @notice Violates A2: anyone can delegatecall arbitrary code as this contract.
contract DangerousProxy {
    function execute(address tgt, bytes calldata data) external returns (bytes memory) {
        (bool ok, bytes memory ret) = tgt.delegatecall(data);
        require(ok, "fail");
        return ret;
    }
}
