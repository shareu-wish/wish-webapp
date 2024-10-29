from flask import Blueprint
import config
import jwt
from flask import request
import db_helper
import phone_verification
import datetime
import payments
import station_controller


api_v1 = Blueprint('api_v1', __name__)


def check_auth():
    """
    Проверка авторизации
    """
    # Get token from Bearer
    authorization_header = request.headers.get("Authorization")
    token = authorization_header.split(" ")[1] if authorization_header else None

    if not token:
        return False

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        return False

    return payload['id']


""" Auth """
@api_v1.route("/auth/start-phone-verification", methods=["POST"])
def auth_start_phone_verification():
    """
    Вызвать flash-звонок
    """
    # TODO: Капча?
    phone = phone_verification.clean_phone(request.form["phone"])
    phone_verification.verify_phone(phone)

    return {"status": "ok"}


@api_v1.route("/auth/check-code", methods=["POST"])
def auth_check_code():
    """
    Проверить код на достоверность и создать пользователя, если его не существует
    """
    phone = phone_verification.clean_phone(request.form["phone"])
    pincode = request.form["code"]
    res = phone_verification.submit_pincode(phone, pincode)

    if res == 'verified':
        user_id = db_helper.get_user_by_phone(phone)
        if not user_id:
            user_id = db_helper.create_raw_user(phone)
        else:
            user_id = user_id['id']
        
        exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365*10)
        encoded_jwt = jwt.encode({"id": user_id, "exp": exp}, config.JWT_SECRET)
        if str(type(encoded_jwt)) == "<class 'bytes'>":
            encoded_jwt = encoded_jwt.decode()
        
        return {"status": "ok", "is_verified": True, "auth_token": encoded_jwt}
    elif res == 'incorrect':
        return {"status": "ok", "is_verified": False, "reason": None}
    elif res == 'attempts_exceeded':
        return {"status": "ok", "is_verified": False, "reason": "attempts_exceeded"}
    elif res == 'timeout_exceeded':
        return {"status": "ok", "is_verified": False, "reason": "timeout_exceeded"}

# TODO: VK auth API

# Stations
@api_v1.route("/stations/get-all-stations")
def get_all_stations():
    """
    Возвращает все станции со всеми данными
    """
    return db_helper.get_stations()


# Orders
@api_v1.route("/orders/take-umbrella", methods=["POST"])
def orders_take_umbrella():
    # TODO: проверить, все ли работает правильно
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    station_id = int(request.form["station_id"])

    can_take = db_helper.get_station(station_id)['can_take']
    if can_take <= 0:
        return {"status": "error", "message": "There are no umbrellas in this station"}
    
    if db_helper.get_active_order(user_id):
        return {"status": "error", "message": "You have an active order"}
    
    # order_id = db_helper.open_order(user_id, station_id)

    # Манипуляции с банками
    payment_token = db_helper.get_user_payment_token(user_id)
    if payment_token:
        got_deposit = payments.make_deposit(user_id, station_id)

        if got_deposit:
            return {"status": "ok", "payment_mode": "auto", "user_id": user_id, "station_id": station_id}
        else:
            db_helper.update_user_payment_token(user_id, None)
            db_helper.update_user_payment_card_last_four(user_id, None)
        
    return {"status": "ok", "payment_mode": "manual", "user_id": user_id, "station_id": station_id}


@api_v1.route("/orders/put-umbrella", methods=["POST"])
def orders_put_umbrella():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    station_id = int(request.form["station_id"])

    can_put = db_helper.get_station(station_id)['can_put']
    if can_put <= 0:
        return {"status": "error", "message": "There are no empty slots in this station"}
    
    active_order = db_helper.get_active_order(user_id)
    if not active_order:
        return {"status": "error", "message": "You have no active orders"}
    order_id = active_order['id']

    # Манипуляции с аппаратной частью станции
    slot = station_controller.put_umbrella(order_id, station_id)

    return {"status": "ok", "slot": slot, "order_id": order_id}
