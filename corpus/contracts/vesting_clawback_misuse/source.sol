// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
contract Vesting {
    address public beneficiary;
    address public funder;
    function setup(address b) external { funder = msg.sender; beneficiary = b; }
    function release() external { payable(beneficiary).transfer(address(this).balance); }
    // BUG: anyone can call clawback
    function clawback() external { payable(funder).transfer(address(this).balance); }
}
