// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract TrustTagged {
    struct PriceTagged {
        uint256 value;
        bool fromOracle;       // explicit trust-source tag
        uint256 receivedAt;
    }
    mapping(address => PriceTagged) public prices;
    address public immutable oracle;
    constructor(address _o) { oracle = _o; }

    function pushPrice(address asset, uint256 v) external {
        require(msg.sender == oracle, "not oracle");
        prices[asset] = PriceTagged({ value: v, fromOracle: true, receivedAt: block.timestamp });
    }

    function read(address asset) external view returns (uint256, bool, uint256) {
        PriceTagged memory p = prices[asset];
        return (p.value, p.fromOracle, p.receivedAt);
    }
}
