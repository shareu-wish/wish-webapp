import requests
import config
import db_helper
import random


url = "https://zvonok.com/manager/cabapi_external/api/v1/phones/flashcall/"


def clean_phone(phone: str) -> str:
    """
    Очистка номера телефона от лишних символов
    :param phone: Номер телефона, который мы очищаем
    :return: Очищенный номер телефона
    """

    return phone.strip().replace("-", "").replace("(", "").replace(")", "").replace(" ", "")


def _init_call(phone: str) -> str:
    """
    Инициализация звонка
    :param phone: Номер телефона, на который поступит звонок
    :return: Пинкод, необходимый для верификации телефона
    """

    data = {
        "public_key": config.ZVONOK_PUBLIC_KEY,
        "campaign_id": config.ZVONOK_CAMPAIGN_ID,
        "phone": phone,
    }

    r = requests.post(url, data=data)

    return r.json()["data"]["pincode"]


def verify_phone(phone: str) -> None:
    """
    Верефикация номера телефона
    :param phone: Номер телефона, на который поступит звонок
    """

    #pincode = _init_call(phone)
    pincode = random.randint(1000, 9999)

    if db_helper.get_verify_phone_record(phone):
        db_helper.update_verify_phone_record(phone, pincode)
    else:
        db_helper.create_verify_phone_record(phone, pincode)


def submit_pincode(phone: str, pincode: str) -> str:
    """
    Подтверждение номера телефона
    :param phone: Номер телефона, который мы верифицируем
    :param pincode: Пинкод, полученный пользователем на телефон
    :return: 
        - `verified` - если веревикация успешна
        - `incorrect` - если пинкод неверен
        - `attempts_exceeded` - если попытки закончились
    """

    real_pincode = db_helper.get_verify_phone_record(phone)[1]
    if pincode != real_pincode:
        attempts = db_helper.increment_attempts(phone)
        if attempts >= 3:
            db_helper.delete_verify_phone_record(phone)
            return 'attempts_exceeded', ''
        
        return 'incorrect', ''
    
    db_helper.delete_verify_phone_record(phone)
    user_id = db_helper.create_raw_user(phone)

    return 'verified', user_id


