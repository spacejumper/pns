// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import {Pausable} from "openzeppelin-contracts/contracts/utils/Pausable.sol";
import {Ownable} from "openzeppelin-contracts/contracts/access/Ownable.sol";

contract MockUSDC is ERC20, Pausable, Ownable {
    mapping(address => bool) public blacklisted;

    constructor(address initialOwner) ERC20("Mock USDC", "mUSDC") Ownable(initialOwner) {}

    function decimals() public pure override returns (uint8) {
        return 6;
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    function blacklist(address account) external onlyOwner {
        blacklisted[account] = true;
    }

    function unBlacklist(address account) external onlyOwner {
        blacklisted[account] = false;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function _update(address from, address to, uint256 value) internal override whenNotPaused {
        require(!blacklisted[from], "sender blacklisted");
        require(!blacklisted[to], "recipient blacklisted");
        super._update(from, to, value);
    }
}
