// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract VisorArchetype {
    function execute(address to, bytes calldata data) external returns (bytes memory) {
        (bool ok, bytes memory ret) = to.delegatecall(data);  // BUG: any code as this contract
        require(ok); return ret;
    }
}
