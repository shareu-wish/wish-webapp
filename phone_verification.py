import requests
import config
import db_helper


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

    pincode = _init_call(phone)
    db_helper.create_verify_phone_record(phone, pincode)


def submit_pincode(phone: str, pincode: str) -> bool:
    """
    Подтверждение номера телефона
    :param phone: Номер телефона, который мы верифицируем
    :param pincode: Пинкод, полученный пользователем на телефон
    :return: True, если номер телефона успешно верифицирован, False в противном случае
    """

    real_pincode = db_helper.get_verify_phone_record(phone)[1]
    if pincode != real_pincode:
        return False
    
    db_helper.delete_verify_phone_record(phone)
    db_helper.create_raw_user(phone)

    return True


