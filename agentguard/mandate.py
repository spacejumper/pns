from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from eth_account import Account
from eth_account.messages import encode_typed_data


MANDATE_DOMAIN = {
    "name": "AgentGuardMandate",
    "version": "1",
    "chainId": 31337,
    "verifyingContract": "0x0000000000000000000000000000000000000001",
}

MANDATE_TYPES = {
    "Mandate": [
        {"name": "user", "type": "address"},
        {"name": "agent", "type": "address"},
        {"name": "max_per_tx", "type": "uint256"},
        {"name": "window_budget", "type": "uint256"},
        {"name": "window_seconds", "type": "uint256"},
        {"name": "expiry", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"},
    ]
}


@dataclass
class SignedMandate:
    mandate: dict[str, Any]
    signature: str


def build_typed_data(mandate: dict[str, Any]) -> dict[str, Any]:
    message = {
        "user": mandate["user"],
        "agent": mandate["agent"],
        "max_per_tx": int(mandate["max_per_tx"]),
        "window_budget": int(mandate["window_budget"]),
        "window_seconds": int(mandate["window_seconds"]),
        "expiry": int(mandate["expiry"]),
        "nonce": mandate["nonce"],
    }
    return {
        "types": {**MANDATE_TYPES, "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ]},
        "domain": MANDATE_DOMAIN,
        "primaryType": "Mandate",
        "message": message,
    }


def sign_mandate(mandate: dict[str, Any], private_key: str) -> SignedMandate:
    typed_data = build_typed_data(mandate)
    signable = encode_typed_data(full_message=typed_data)
    signed = Account.sign_message(signable, private_key=private_key)
    return SignedMandate(mandate=mandate, signature=signed.signature.hex())


def verify_mandate(signed: SignedMandate) -> tuple[bool, str]:
    mandate = signed.mandate
    if int(mandate["expiry"]) <= int(time.time()):
        return False, "mandate_expired"

    typed_data = build_typed_data(mandate)
    signable = encode_typed_data(full_message=typed_data)
    recovered = Account.recover_message(signable, signature=signed.signature)
    if recovered.lower() != mandate["user"].lower():
        return False, "mandate_bad_signature"
    return True, "ok"
