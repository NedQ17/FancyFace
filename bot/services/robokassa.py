import hashlib
from urllib.parse import urlencode

from bot.config import (
    ROBOKASSA_LOGIN,
    ROBOKASSA_PASSWORD1, ROBOKASSA_PASSWORD2,
    ROBOKASSA_TEST_PASSWORD1, ROBOKASSA_TEST_PASSWORD2,
    ROBOKASSA_IS_TEST,
    ROBOKASSA_RESULT_URL,
)

# В тестовом режиме используются отдельные тестовые пароли (см. Технические настройки Robokassa)
_pwd1 = ROBOKASSA_TEST_PASSWORD1 if ROBOKASSA_IS_TEST else ROBOKASSA_PASSWORD1
_pwd2 = ROBOKASSA_TEST_PASSWORD2 if ROBOKASSA_IS_TEST else ROBOKASSA_PASSWORD2

_PAYMENT_URL = "https://auth.robokassa.ru/Merchant/Index.aspx"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest().upper()


def build_payment_url(payment_id: int, amount_rub: float, description: str, user_id: int) -> str:
    out_sum = f"{amount_rub:.2f}"
    inv_id = str(payment_id)
    shp_uid = str(user_id)

    sig_str = f"{ROBOKASSA_LOGIN}:{out_sum}:{inv_id}:{_pwd1}:Shp_uid={shp_uid}"
    signature = _md5(sig_str)

    params: dict = {
        "MerchantLogin": ROBOKASSA_LOGIN,
        "OutSum": out_sum,
        "InvId": inv_id,
        "Description": description,
        "SignatureValue": signature,
        "Shp_uid": shp_uid,
        "Culture": "ru",
    }
    if ROBOKASSA_RESULT_URL:
        params["ResultUrl"] = ROBOKASSA_RESULT_URL
    if ROBOKASSA_IS_TEST:
        params["IsTest"] = "1"

    return f"{_PAYMENT_URL}?{urlencode(params)}"


def verify_result(out_sum: str, inv_id: str, signature: str, shp_uid: str) -> bool:
    sig_str = f"{out_sum}:{inv_id}:{_pwd2}:Shp_uid={shp_uid}"
    return _md5(sig_str) == signature.upper()
