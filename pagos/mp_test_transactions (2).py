#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPE DE PRUEBAS MERCADO PAGO (PERÚ)
-----------------------------------
[A] Checkout Pro (por link) -> usa APP_USR del VENDEDOR DE PRUEBA
    - Genera preferencias y URLs sandbox (payer se loguea y paga con Dinero en cuenta).
[B] Checkout API (automatizado) -> usa TEST- (no APP_USR)
    - Tokeniza tarjetas de prueba (APRO) y crea pagos directos.

IMPORTANTE:
- APP_USR (de vendedor de prueba) sirve en sandbox para Checkout Pro.
- Para Checkout API con tarjetas sandbox, NO usar APP_USR: usar TEST-.
  Si usas APP_USR en API, verás: 401 "Unauthorized use of live credentials".

Requisitos:
  pip install mercadopago requests
"""

import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List

import requests
import mercadopago


# ──────────────────────────────────────────────────────────────
# CREDENCIALES QUE ME PASASTE
# ──────────────────────────────────────────────────────────────
# Vendedores de PRUEBA (APP_USR = credenciales "live" de usuario de prueba)
VENDOR_1_APP_USR = "APP_USR-4354595753247237-082211-20ce3c9a0a515bc50314299f89784c7f-2644086260"
VENDOR_2_APP_USR = "APP_USR-8982691557495367-082211-69cd81eda52f7857c5e0237abf7d07f6-2638682199"

# Para Checkout API (automatizado) DEBES usar TEST- (el de tu negocio ya funciona)
BUSINESS_TEST_TOKEN = "TEST-6717023677658234-082111-a7fa92c3a2f98ba38957b9be0052faa7-2627767616"

# Elige vendedor para Checkout Pro
USE_VENDOR = 1  # 1 -> vendor 1, 2 -> vendor 2


# ──────────────────────────────────────────────────────────────
# ENTIDADES SIMULADAS (como modelo de BD)
# ──────────────────────────────────────────────────────────────
@dataclass
class Credentials:
    access_token: str


@dataclass
class User:
    user_id: int
    nickname: str
    email: str
    role: str  # "seller" | "buyer"
    credentials: Optional[Credentials] = None


# “Base de datos” mínima en memoria
VENDOR_1 = User(
    user_id=2644086260,
    nickname="TESTUSER9069997784260511657",
    email="test_user_9069997784260511657@testuser.com",
    role="seller",
    credentials=Credentials(access_token=VENDOR_1_APP_USR),
)

VENDOR_2 = User(
    user_id=2638682199,
    nickname="TESTUSER2960386160311913342",
    email="test_user_2960386160311913342@testuser.com",
    role="seller",
    credentials=Credentials(access_token=VENDOR_2_APP_USR),
)

# Compradores de prueba (los que me diste)
BUYER_1 = User(
    user_id=2638680161,
    nickname="TESTUSER2385310033375255184",
    email="test_user_2385310033375255184@testuser.com",
    role="buyer",
)
BUYER_2 = User(
    user_id=2638680653,
    nickname="TESTUSER8084593226901106186",
    email="test_user_8084593226901106186@testuser.com",
    role="buyer",
)

# Para API: para evitar 403 “Payer email forbidden” con TEST-, usamos emails “seguros”
SAFE_EMAILS = {
    BUYER_1.user_id: "comprador1@example.com",
    BUYER_2.user_id: "comprador2@example.com",
}

# Tarjetas de prueba (Perú) + “APRO” para forzar aprobado en sandbox
TEST_CARDS = {
    "visa":   {"number": "4009175332806176", "security_code": "123",  "exp_month": 11, "exp_year": 2030},
    "master": {"number": "5031755734530604", "security_code": "123",  "exp_month": 11, "exp_year": 2030},
    "amex":   {"number": "371180303257522",  "security_code": "1234", "exp_month": 11, "exp_year": 2030},
}
CARDHOLDER_NAME = "APRO"
CARDHOLDER_DOC  = "123456789"

# Escenarios
SCENARIOS_PRO: List[tuple] = [
    # (buyer, amount, title)
    (BUYER_1, 120.50, "Compra con saldo (C1)"),
    (BUYER_2,  75.25, "Compra con saldo (C2)"),
    (BUYER_1, 305.00, "Compra con saldo (C1)"),
    (BUYER_2, 149.49, "Compra con saldo (C2)"),
]
SCENARIOS_API: List[tuple] = [
    # (buyer, amount, method)
    (BUYER_1, 120.50, "visa"),
    (BUYER_2,  75.25, "visa"),
    (BUYER_1,  42.00, "master"),
    (BUYER_2, 199.90, "amex"),
]

LOG_PRO = "log_checkout_pro_urls.csv"
LOG_API = "log_checkout_api_payments.csv"


# ──────────────────────────────────────────────────────────────
# HELPERS HTTP/SDK
# ──────────────────────────────────────────────────────────────
def whoami(token: str) -> dict:
    r = requests.get(
        "https://api.mercadopago.com/users/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    if r.status_code != 200:
        raise RuntimeError(f"/users/me failed: HTTP {r.status_code} - {r.text}")
    return r.json()


def build_sdk(token: str) -> mercadopago.SDK:
    return mercadopago.SDK(token)


def init_csv(path: str, headers: List[str]):
    try:
        with open(path, "r", encoding="utf-8"):
            return
    except FileNotFoundError:
        pass
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()


# ──────────────────────────────────────────────────────────────
# [A] CHECKOUT PRO (APP_USR del vendedor de prueba)
# ──────────────────────────────────────────────────────────────
def create_preference_for_account_money(sdk: mercadopago.SDK, title: str, amount_pen: float, buyer_email: str) -> dict:
    """
    Creamos una preferencia restringiendo medios a 'account_money'.
    El comprador se loguea con su cuenta de prueba y paga con su saldo.
    """
    pref = {
        "items": [{
            "title": title,
            "quantity": 1,
            "currency_id": "PEN",
            "unit_price": round(float(amount_pen), 2),
        }],
        "payer": {"email": buyer_email},
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "credit_card"},
                {"id": "debit_card"},
                {"id": "prepaid_card"},
                {"id": "ticket"},
                {"id": "bank_transfer"},
                {"id": "atm"},
                {"id": "digital_currency"},
            ],
            "installments": 1,
            "default_payment_type_id": "account_money",
        },
        "back_urls": {
            "success": "https://example.com/success",
            "failure": "https://example.com/failure",
            "pending": "https://example.com/pending",
        },
        "auto_return": "approved",
        "statement_descriptor": "MP TEST",
    }
    res = sdk.preference().create(pref)
    if res.get("status") not in (200, 201):
        raise RuntimeError(f"Preference create failed: HTTP {res.get('status')} - {res.get('response')}")
    return res["response"]


def run_checkout_pro_demo(collector: User, buyers: List[User]):
    if not collector.credentials or not collector.credentials.access_token.startswith("APP_USR-"):
        raise RuntimeError("Para Checkout Pro necesitas APP_USR del vendedor de PRUEBA.")

    # Validación suave
    me = whoami(collector.credentials.access_token)
    print(f"[whoami] collector -> id={me.get('id')} nick={me.get('nickname')} site={me.get('site_id')}")

    sdk = build_sdk(collector.credentials.access_token)
    init_csv(LOG_PRO, ["timestamp", "buyer_nick", "buyer_email", "amount", "title", "preference_id", "sandbox_url"])

    print("\n=== [A] Checkout Pro (por link, Dinero en cuenta) ===")
    for i, (buyer, amount, title) in enumerate(SCENARIOS_PRO, start=1):
        pref = create_preference_for_account_money(sdk, title=title, amount_pen=amount, buyer_email=buyer.email)
        pref_id = pref.get("id")
        url = pref.get("sandbox_init_point") or pref.get("init_point")
        print("--------------------------------------------------------------------")
        print(f"{i:02d}) {buyer.nickname} | {buyer.email} | PEN {amount:.2f}")
        print(f"     Preference ID: {pref_id}")
        print(f"     Abrir (SANDBOX): {url}")

        with open(LOG_PRO, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=[
                "timestamp", "buyer_nick", "buyer_email", "amount", "title", "preference_id", "sandbox_url"
            ]).writerow({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "buyer_nick": buyer.nickname,
                "buyer_email": buyer.email,
                "amount": amount,
                "title": title,
                "preference_id": pref_id,
                "sandbox_url": url,
            })


# ──────────────────────────────────────────────────────────────
# [B] CHECKOUT API (automatizado) — REQUIERE TEST-
# ──────────────────────────────────────────────────────────────
def create_card_token(sdk: mercadopago.SDK, method: str) -> str:
    card = TEST_CARDS[method]
    payload = {
        "card_number": card["number"],
        "security_code": card["security_code"],
        "expiration_month": card["exp_month"],
        "expiration_year": card["exp_year"],
        "cardholder": {
            "name": CARDHOLDER_NAME,  # "APRO" => aprobado
            "identification": {"type": "DNI", "number": CARDHOLDER_DOC},
        },
    }
    res = sdk.card_token().create(payload)
    if res["status"] not in (200, 201):
        raise RuntimeError(f"Card token creation failed: HTTP {res['status']} - {res.get('response')}")
    return res["response"]["id"]


def create_payment(sdk: mercadopago.SDK, amount: float, token_id: str, method_id: str, buyer_email: str) -> dict:
    """
    Función con la firma “exacta” que pediste.
    """
    data = {
        "transaction_amount": round(float(amount), 2),
        "token": token_id,
        "description": "Test Payment via SDK - API",
        "installments": 1,
        "payment_method_id": method_id,  # "visa" | "master" | "amex"
        "payer": {"email": buyer_email, "identification": {"type": "DNI", "number": "12345678"}},
        "binary_mode": False,
    }
    return sdk.payment().create(data)


def run_checkout_api_demo(api_collector_test_token: str, buyers: List[User]):
    """
    Para evitar 401, este flujo EXIGE un TEST-...
    Si pasas APP_USR aquí, verás "Unauthorized use of live credentials".
    """
    if not api_collector_test_token.startswith("TEST-"):
        raise RuntimeError("Checkout API requiere TEST- (no APP_USR). Pasa BUSINESS_TEST_TOKEN u otro TEST- válido.")

    me = whoami(api_collector_test_token)
    print(f"\n[whoami] API collector (TEST-) -> id={me.get('id')} nick={me.get('nickname')} site={me.get('site_id')}")

    sdk = build_sdk(api_collector_test_token)
    init_csv(LOG_API, [
        "timestamp", "buyer_nick", "buyer_real_email", "payer_email_sent", "amount", "method",
        "http", "payment_id", "status", "status_detail", "net_received_amount", "error",
    ])

    print("\n=== [B] Checkout API (automatizado, sin link) ===")
    for i, (buyer, amount, method) in enumerate(SCENARIOS_API, start=1):
        payer_email = SAFE_EMAILS.get(buyer.user_id, f"{buyer.nickname.lower()}@example.com")
        try:
            token_id = create_card_token(sdk, method)
            res = create_payment(sdk, amount, token_id, method, payer_email)
            http_status = res.get("status")
            body = res.get("response", {})
            status = body.get("status")
            status_detail = body.get("status_detail")
            net = body.get("transaction_details", {}).get("net_received_amount")

            print("--------------------------------------------------------------------")
            print(f"{i:02d}) {buyer.nickname} -> {method.upper()} -> PEN {amount:.2f}")
            print(f"     payer_email_enviado: {payer_email}")
            print(f"     HTTP: {http_status} | status: {status} | detail: {status_detail}")
            print("     Response:", json.dumps(body, indent=2, ensure_ascii=False))

            with open(LOG_API, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=[
                    "timestamp", "buyer_nick", "buyer_real_email", "payer_email_sent", "amount", "method",
                    "http", "payment_id", "status", "status_detail", "net_received_amount", "error",
                ]).writerow({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "buyer_nick": buyer.nickname,
                    "buyer_real_email": buyer.email,
                    "payer_email_sent": payer_email,
                    "amount": amount,
                    "method": method,
                    "http": http_status,
                    "payment_id": body.get("id"),
                    "status": status,
                    "status_detail": status_detail,
                    "net_received_amount": net,
                    "error": "",
                })

        except Exception as e:
            print("--------------------------------------------------------------------")
            print(f"{i:02d}) {buyer.nickname} -> {method.upper()} -> PEN {amount:.2f}")
            print(f"     payer_email_enviado: {payer_email}")
            print(f"     ERROR: {e}")
            with open(LOG_API, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=[
                    "timestamp", "buyer_nick", "buyer_real_email", "payer_email_sent", "amount", "method",
                    "http", "payment_id", "status", "status_detail", "net_received_amount", "error",
                ]).writerow({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "buyer_nick": buyer.nickname,
                    "buyer_real_email": buyer.email,
                    "payer_email_sent": payer_email,
                    "amount": amount,
                    "method": method,
                    "http": None,
                    "payment_id": None,
                    "status": None,
                    "status_detail": None,
                    "net_received_amount": None,
                    "error": str(e),
                })


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    # Elegimos el vendedor para Checkout Pro
    collector_for_links = VENDOR_1 if USE_VENDOR == 1 else VENDOR_2

    # [A] Checkout Pro con APP_USR (URLs sandbox)
    run_checkout_pro_demo(collector_for_links, [BUYER_1, BUYER_2])

    # [B] Checkout API con TEST- (pagos directos)
    #    Si aquí usas APP_USR te dará 401. Por eso usamos tu TEST- del negocio.
    run_checkout_api_demo(BUSINESS_TEST_TOKEN, [BUYER_1, BUYER_2])

    print("\n=== FIN DEL PIPE ===")
    print(f"- URLs de Checkout Pro en: ./{LOG_PRO}")
    print(f"- Resultados de Checkout API en: ./{LOG_API}")


if __name__ == "__main__":
    main()
