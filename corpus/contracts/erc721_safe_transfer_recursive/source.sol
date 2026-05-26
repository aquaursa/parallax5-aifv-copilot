// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;
interface IReceiver { function onERC721Received(address,address,uint256,bytes calldata) external returns (bytes4); }
contract ERC721Vuln {
    mapping(uint256 => address) public ownerOf;
    function safeTransferFrom(address from, address to, uint256 id) external {
        require(ownerOf[id] == from);
        // BUG: callback before ownerOf update
        IReceiver(to).onERC721Received(msg.sender, from, id, "");
        ownerOf[id] = to;
    }
}
