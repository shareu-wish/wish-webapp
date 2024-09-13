import config
import hashlib
import hmac
import base64
import db_helper
import requests
import json


CLOUD_PAYMENTS_PUBLIC_ID = config.CLOUD_PAYMENTS_PUBLIC_ID
CLOUD_PAYMENTS_SECRET_KEY = config.CLOUD_PAYMENTS_SECRET_KEY
CLOUD_PAYMENTS_BASIC_AUTH = config.CLOUD_PAYMENTS_BASIC_AUTH
DEPOSIT_AMOUNT = config.DEPOSIT_AMOUNT


def is_notification_valid(val_code, raw_data) -> bool:
    """
    Проверяет подлинность pay-уведомления
    """
    code = hmac.new(CLOUD_PAYMENTS_SECRET_KEY.encode('utf-8'), raw_data.encode('utf-8'), hashlib.sha256).digest()
    code = base64.b64encode(code).decode()
    return val_code == code


def make_deposit(user_id, station_id) -> bool:
    """
    Создать депозит от конктерного пользователя
    """
    payment_token = db_helper.get_user_payment_token(user_id)

    order = db_helper.get_active_order(user_id)
    if order:
        return
    
    r = requests.post(
        "https://api.cloudpayments.ru/payments/tokens/auth",
        headers={
            "Authorization": f"Basic {CLOUD_PAYMENTS_BASIC_AUTH}"
        },
        data={
            "Amount": DEPOSIT_AMOUNT,
            "Currency": "RUB",
            "Description": "Депозит за зонт — WISH",
            "AccountId": user_id,
            # "InvoiceId": order['id'],
            "TrInitiatorCode": 0,
            "PaymentScheduled": 0,
            "Token": payment_token,
            "JsonData": json.dumps({
                "stationTake": station_id,
                "paymentMode": "auto"
            }),
        },
    )

    data = r.json()
    if data['Success']:
        # db_helper.set_order_deposit_tx_id(order['id'], data['Model']['TransactionId'])
        return True
    else:
        return False


def burn_deposit(user_id) -> bool:
    order = db_helper.get_active_order(user_id)
    deposit_tx_id = order['deposit_tx_id']
    if not deposit_tx_id:
        return
    
    r = requests.post(
        "https://api.cloudpayments.ru/payments/confirm",
        headers={
            "Authorization": f"Basic {CLOUD_PAYMENTS_BASIC_AUTH}"
        },
        data={
            "TransactionId": deposit_tx_id,
            "Amount": DEPOSIT_AMOUNT
        },
    )

    data = r.json()
    return data['Success']


def refund_deposit_by_tx_id(tx_id) -> bool:
    """
    Вернуть депозит (по ID транзакции)
    """
    r = requests.post(
        "https://api.cloudpayments.ru/payments/void",
        headers={
            "Authorization": f"Basic {CLOUD_PAYMENTS_BASIC_AUTH}"
        },
        data={
            "TransactionId": tx_id
        },
    )

    data = r.json()
    return data['Success']


def refund_deposit(user_id) -> bool:
    """
    Вернуть депозит пользователю
    """
    order = db_helper.get_active_order(user_id)
    if not order:
        return False
    deposit_tx_id = order['deposit_tx_id']
    if not deposit_tx_id:
        return False

    return refund_deposit_by_tx_id(deposit_tx_id)


def write_off_for_delay(user_id, order_id) -> bool:
    """
    Списать штраф за несданный зонт
    """
    payment_token = db_helper.get_user_payment_token(user_id)

    r = requests.post(
        "https://api.cloudpayments.ru/payments/tokens/charge",
        headers={
            "Authorization": f"Basic {CLOUD_PAYMENTS_BASIC_AUTH}"
        },
        data={
            "Amount": DEPOSIT_AMOUNT,
            "Currency": "RUB",
            "Description": "Штраф за несданный зонт — WISH",
            "AccountId": user_id,
            "InvoiceId": order_id,
            "TrInitiatorCode": 0,
            "PaymentScheduled": 0,
            "Token": payment_token,
        },
    )

    data = r.json()
    return data['Success']
    
