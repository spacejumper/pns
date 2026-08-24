// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script} from "forge-std/Script.sol";
import {console2} from "forge-std/console2.sol";
import {MockUSDC} from "../src/MockUSDC.sol";
import {GuardedWallet} from "../src/GuardedWallet.sol";

contract Deploy is Script {
    function run() external {
        uint256 deployerPk = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPk);

        address owner = vm.addr(deployerPk);
        MockUSDC token = new MockUSDC(owner);
        GuardedWallet wallet = new GuardedWallet(owner, address(token), 200_000000, 500_000000, 1 days);

        token.mint(address(wallet), 1_000_000000);

        vm.stopBroadcast();

        console2.log("MockUSDC:", address(token));
        console2.log("GuardedWallet:", address(wallet));
    }
}
