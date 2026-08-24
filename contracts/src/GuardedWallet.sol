// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "openzeppelin-contracts/contracts/access/Ownable.sol";

contract GuardedWallet is Ownable {
    IERC20 public immutable usdc;

    uint256 public maxPerTx;
    uint256 public windowBudget;
    uint256 public windowSeconds;
    uint256 public windowStart;
    uint256 public windowSpent;
    bool public tripped;

    event PaymentExecuted(address indexed to, uint256 amount, bytes32 memoHash);
    event BreakerTripped(address indexed by);
    event BreakerReset(address indexed by);

    constructor(
        address initialOwner,
        address usdcToken,
        uint256 _maxPerTx,
        uint256 _windowBudget,
        uint256 _windowSeconds
    ) Ownable(initialOwner) {
        usdc = IERC20(usdcToken);
        maxPerTx = _maxPerTx;
        windowBudget = _windowBudget;
        windowSeconds = _windowSeconds;
        windowStart = block.timestamp;
    }

    modifier notTripped() {
        require(!tripped, "breaker tripped");
        _;
    }

    function setLimits(uint256 _maxPerTx, uint256 _windowBudget, uint256 _windowSeconds) external onlyOwner {
        maxPerTx = _maxPerTx;
        windowBudget = _windowBudget;
        windowSeconds = _windowSeconds;
    }

    function trip() external onlyOwner {
        tripped = true;
        emit BreakerTripped(msg.sender);
    }

    function reset() external onlyOwner {
        tripped = false;
        emit BreakerReset(msg.sender);
    }

    function _rollWindow() internal {
        if (block.timestamp >= windowStart + windowSeconds) {
            windowStart = block.timestamp;
            windowSpent = 0;
        }
    }

    function executePayment(address to, uint256 amount, bytes32 memoHash) external onlyOwner notTripped {
        _rollWindow();
        require(amount <= maxPerTx, "maxPerTx exceeded");
        require(windowSpent + amount <= windowBudget, "window budget exceeded");

        windowSpent += amount;
        bool ok = usdc.transfer(to, amount);
        require(ok, "transfer failed");

        emit PaymentExecuted(to, amount, memoHash);
    }
}
