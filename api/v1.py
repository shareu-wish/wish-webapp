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
    phone = phone_verification.clean_phone(request.json["phone"])
    phone_verification.verify_phone(phone)

    return {"status": "ok"}


@api_v1.route("/auth/check-code", methods=["POST"])
def auth_check_code():
    """
    Проверить код на достоверность и создать пользователя, если его не существует
    """
    phone = phone_verification.clean_phone(request.json["phone"])
    pincode = request.json["code"]
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
    
    station_id = int(request.json["station_id"])

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
    
    station_id = int(request.json["station_id"])

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


@api_v1.route("/orders/get-order-status")
def orders_get_order_status():
    """
    Получить текущий статус текущего заказа (если нет текущего, статус последнего заказа)
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    """
    station_opened_to_take - слот открыт для взятия зонта
    station_opened_to_put - слот открыт для возврата зонта
    in_the_hands - зонт взят, находится у пользователя
    closed_successfully - зонт возвращен, заказ закрыт
    timeout_exceeded - время ожидания взятия зонта истекло
    bank_error - ошибка банка, оплата не прошла
    unknown - что-то пошло не так
    """
    
    active_order = db_helper.get_active_order(user_id)
    if active_order:
        timeout = db_helper.get_station_lock_timeout_by_order_id(active_order['id'])
        if timeout:
            if timeout['type'] == 1:
                return {"status": "ok", "order_status": "station_opened_to_take", "slot": timeout['slot']}
            elif timeout['type'] == 2:
                return {"status": "ok", "order_status": "station_opened_to_put", "slot": timeout['slot']}
            else:
                return {"status": "ok", "order_status": "unknown"}
        else:
            return {"status": "ok", "order_status": "in_the_hands"}
    else:
        last_order = db_helper.get_last_order(user_id)
        order_status = ""
        if last_order is None:
            order_status = "unknown"
        elif last_order['state'] == 0:
            order_status = "closed_successfully"
        elif last_order['state'] == 2:
            order_status = "timeout_exceeded"
        elif last_order['state'] == 3:
            order_status = "bank_error"
        else:
            order_status = "unknown"
        
        return {"status": "ok", "order_status": order_status}
    

@api_v1.route("/orders/feedback", methods=["POST"])
def orders_feedback():
    """
    Оставить отзыв на последний заказ
    """
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    order_id = db_helper.get_last_order(user_id)['id']
    rate = request.json["rate"]
    text = request.json["text"]

    if rate < 1 or rate > 5:
        return {"status": "error", "message": "Invalid rate"}
    if db_helper.has_user_feedback(user_id, order_id):
        return {"status": "error", "message": "Feedback for this order has already been left"}

    db_helper.create_order_feedback(user_id, order_id, rate, text)

    return {"status": "ok"}


# Profile
@api_v1.route('/profile/get-user-info')
def profile_get_user_info():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    data = db_helper.get_user(user_id)
    res = {
        "id": data['id'],
        "phone": data['phone'],
        "name": data['name'],
        "gender": data['gender'],
        "age": data['age'],
        "payment_card_last_four": data['payment_card_last_four']
    }
    return res


@api_v1.route('/profile/update-user-info', methods=['POST'])
def profile_update_user_info():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    data = request.get_json(force=True)
    db_helper.update_user_info(user_id, data)
    
    return {"status": "ok"}


@api_v1.route("/profile/get-active-order")
def profile_get_active_order():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "order": None}

    order = db_helper.get_active_order(user_id)
    if not order:
        return {"status": "ok", "order": None}

    return {"status": "ok", "order": order}


@api_v1.route("/profile/get-processed-orders")
def profile_get_processed_orders():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "orders": []}

    orders = db_helper.get_processed_orders(user_id)
    if not orders:
        return {"status": "ok", "orders": []}
    
    for i in range(len(orders)):
        orders[i]['station_take_address'] = db_helper.get_station(orders[i]['station_take'])['address']
        orders[i]['station_put_address'] = db_helper.get_station(orders[i]['station_put'])['address']

    return {"status": "ok", "orders": orders}


# Subscription
@api_v1.route("/subscription/get-subscription-info")
def get_subscription_info():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}

    subscription = db_helper.get_user_subscription(user_id)

    users = []
    for user_id in subscription['family_members']:
        user = {"id": user_id}
        user_db = db_helper.get_user(user_id)
        user["phone"] = user_db['phone']
        user["name"] = user_db['name']
        users.append(user)
    subscription['family_members'] = users

    return {"status": "ok", "subscription": subscription}


@api_v1.route("/subscription/send-invitation", methods=["POST"])
def subscription_send_invitation():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "code": "unauthorized", "message": "Unauthorized"}
    
    phone = phone_verification.clean_phone(request.json["phone"])
    recipient = db_helper.get_user_by_phone(phone)
    if not recipient:
        return {"status": "error", "code": "user_not_found", "message": "User with this phone number does not exist"}
    
    # check if recipient is already in the family
    subscription = db_helper.get_user_subscription(recipient['id'])
    if subscription:
        if recipient['id'] == subscription['owner']:
            return {"status": "error", "code": "user_already_has_subscription", "message": "User is already has a subscription"}
        else:
            return {"status": "error", "code": "user_already_in_family", "message": "User is already in the family"}
    
    # check if user has already sent an invitation to this user
    other_invitations = db_helper.find_user_subscription_invitations(recipient['id'])
    if not all(invitation['owner'] != user_id for invitation in other_invitations):
        return {"status": "error", "code": "invitation_already_sent", "message": "Invitation to this user has already been sent"}
    
    # check if sum of family members + invitations is not greater than 3
    current_user_subscription = db_helper.get_user_subscription(user_id)
    family_members = current_user_subscription['family_members']
    invitations = db_helper.find_subscription_invitations_by_subscription_id(current_user_subscription['id'])
    if len(family_members) + len(invitations) > config.MAX_FAMILY_MEMBERS:
        return {"status": "error", "code": "family_members_limit_reached", "message": "Family members limit reached"}
    
    db_helper.create_subscription_invitation(user_id, recipient['id'])
    return {"status": "ok"}
