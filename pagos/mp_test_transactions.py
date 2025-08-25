#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mercado Pago - Checkout API Test Runner (Peru)
------------------------------------------------
- Creates card tokens for MP test cards
- Triggers payments with different outcomes by using special cardholder names (APRO, OTHE, CONT, CALL, FUND, SECU, EXPI, FORM)
- Saves a CSV log of attempts in ./mp_test_logs.csv

Usage:
  pip install mercadopago python-dotenv
  # Option A: provide credentials via env (.env file or shell)
  export MP_ACCESS_TOKEN="TEST-xxxxxxxxxxxxxxxx"
  export MP_PUBLIC_KEY="TEST-xxxxxxxxxxxxxxxx"
  # Option B: edit the DEFAULT_* constants below

  # Single scenario
  python mp_test_transactions.py --status APRO --method visa --amount 10.5

  # Run all key scenarios
  python mp_test_transactions.py --run-all

Note:
- This is for TEST environment only.
- For Peru, identification type usually "DNI"; number per MP docs for testing.
"""

import os
import sys
import csv
import json
import time
import argparse
from datetime import datetime

try:
    import mercadopago
except ImportError:
    print("Missing dependency: mercadopago. Install with 'pip install mercadopago'")
    sys.exit(1)

# ======= Credentials =======
DEFAULT_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "TEST-6717023677658234-082111-a7fa92c3a2f98ba38957b9be0052faa7-2627767616")
DEFAULT_PUBLIC_KEY   = os.getenv("MP_PUBLIC_KEY",   "TEST-5b04c74f-3229-4d1e-8e8f-7997c830c37b")

# ======= Test cards (Perú) =======
TEST_CARDS = {
    "visa": {
        "number": "4009175332806176",
        "security_code": "123",
        "exp_month": 11,
        "exp_year": 2030,
    },
    "master": {
        "number": "5031755734530604",
        "security_code": "123",
        "exp_month": 11,
        "exp_year": 2030,
    },
    "amex": {
        "number": "371180303257522",
        "security_code": "1234",
        "exp_month": 11,
        "exp_year": 2030,
    },
}

# ======= Status mapping (by cardholder name) =======
# MP behavior: set the cardholder.name to one of these to simulate outcomes
STATUS_CARDHOLDER = {
    "APRO": {"name": "APRO", "doc": "123456789"},
    "OTHE": {"name": "OTHE", "doc": "123456789"},
    "CONT": {"name": "CONT", "doc": "123456789"},
    "CALL": {"name": "CALL", "doc": "123456789"},
    "FUND": {"name": "FUND", "doc": "123456789"},
    "SECU": {"name": "SECU", "doc": "123456789"},
    "EXPI": {"name": "EXPI", "doc": "123456789"},
    "FORM": {"name": "FORM", "doc": "123456789"},
}

LOG_FILE = "mp_test_logs.csv"


def build_sdk(access_token: str) -> mercadopago.SDK:
    return mercadopago.SDK(access_token)


def create_card_token(sdk: mercadopago.SDK, public_key: str, card_info: dict, status_key: str) -> str:
    """Create a card token using raw test card data and the special cardholder name."""
    if status_key not in STATUS_CARDHOLDER:
        raise ValueError(f"Unsupported status '{status_key}'. Use one of: {', '.join(STATUS_CARDHOLDER.keys())}")

    holder = STATUS_CARDHOLDER[status_key]
    # Tokenization endpoint (public_key-based). SDK handles host selection.
    payload = {
        "card_number": card_info["number"],
        "security_code": card_info["security_code"],
        "expiration_month": card_info["exp_month"],
        "expiration_year": card_info["exp_year"],
        "cardholder": {
            "name": holder["name"],
            "identification": {
                "type": "DNI",
                "number": holder["doc"],
            },
        },
    }

    # The SDK exposes card_token().create using the Access Token; for proper tokenization flow,
    # we can use the 'payment_methods/card_tokens' resource. The SDK uses private auth,
    # which works in sandbox for tests.
    result = sdk.card_token().create(payload)
    if result["status"] not in (200, 201):
        raise RuntimeError(f"Card token creation failed: HTTP {result['status']} - {result.get('response')}")

    token_id = result["response"]["id"]
    return token_id


def create_payment(sdk: mercadopago.SDK, amount: float, token_id: str, payment_method_id: str, email: str) -> dict:
    """Create a payment using a previously created card token."""
    payment_data = {
        "transaction_amount": round(float(amount), 2),
        "token": token_id,
        "description": "Test Payment via SDK",
        "installments": 1,
        "payment_method_id": payment_method_id,  # "visa", "master", "amex"
        "payer": {
            "email": email,
            "identification": {"type": "DNI", "number": "12345678"},
        },
        "binary_mode": False,  # set True if you only want approved/declined (no pending)
    }
    res = sdk.payment().create(payment_data)
    return res


def log_result(row: dict):
    exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def run_scenario(access_token: str, public_key: str, method_key: str, status_key: str, amount: float):
    method_key = method_key.lower()
    if method_key == "mastercard":
        method_key = "master"
    if method_key not in TEST_CARDS:
        raise ValueError(f"Unsupported method '{method_key}'. Use one of: visa, master, amex")

    sdk = build_sdk(access_token)

    # Create token
    token_id = create_card_token(sdk, public_key, TEST_CARDS[method_key], status_key)

    # Create payment
    payer_email = f"test_user_{int(time.time())}@testuser.com"
    pay_res = create_payment(sdk, amount, token_id, "master" if method_key == "master" else method_key, payer_email)

    http_status = pay_res.get("status")
    response = pay_res.get("response", {})

    # Pull common fields if present
    payment_id = response.get("id")
    status = response.get("status")
    status_detail = response.get("status_detail")
    error_msg = response.get("message") or response.get("error") or ""

    # Print + Log
    print("=" * 60)
    print(f"Scenario -> Method: {method_key} | Status tag: {status_key} | Amount: {amount}")
    print(f"HTTP: {http_status}")
    print("Response:", json.dumps(response, indent=2, ensure_ascii=False))
    print("=" * 60)

    log_row = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method_key,
        "status_tag": status_key,
        "amount": amount,
        "http": http_status,
        "payment_id": payment_id,
        "mp_status": status,
        "mp_status_detail": status_detail,
        "error": error_msg,
    }
    log_result(log_row)


def run_all(access_token: str, public_key: str, amount: float):
    scenarios = [
        ("visa", "APRO"),
        ("master", "APRO"),
        ("amex", "APRO"),
        ("visa", "FUND"),
        ("visa", "SECU"),
        ("visa", "EXPI"),
        ("visa", "CALL"),
        ("visa", "OTHE"),
        ("visa", "FORM"),
        ("visa", "CONT"),
    ]
    for method, status in scenarios:
        try:
            run_scenario(access_token, public_key, method, status, amount)
        except Exception as e:
            print(f"[WARN] Scenario {method}-{status} failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Mercado Pago Checkout API Test Runner (Peru)")
    parser.add_argument("--access-token", default=DEFAULT_ACCESS_TOKEN, help="MP Access Token (TEST)")
    parser.add_argument("--public-key", default=DEFAULT_PUBLIC_KEY, help="MP Public Key (TEST)")
    parser.add_argument("--method", choices=["visa", "master", "mastercard", "amex"], default="visa", help="Card brand")
    parser.add_argument("--status", choices=list(STATUS_CARDHOLDER.keys()), default="APRO", help="Desired test outcome")
    parser.add_argument("--amount", type=float, default=10.0, help="Transaction amount")
    parser.add_argument("--run-all", action="store_true", help="Run a battery of scenarios")

    args = parser.parse_args()

    if not args.access_token.startswith("TEST-"):
        print("WARNING: Access token does not look like a TEST token. Make sure you are not using PRODUCTION.", file=sys.stderr)

    if args.run_all:
        run_all(args.access_token, args.public_key, args.amount)
    else:
        run_scenario(args.access_token, args.public_key, args.method, args.status, args.amount)

    print(f"\nLog saved to ./{LOG_FILE}")


if __name__ == "__main__":
    main()
