from flask import Flask, redirect, make_response, send_from_directory
from flask import render_template
import config
from waitress import serve
import phone_verification
from flask import request
import jwt
import datetime
import db_helper
import station_controller
import payments
import json
import vk_id_auth as vk_id


app = Flask(__name__)


def check_auth():
    """
    Проверка авторизации
    """
    token = request.cookies.get("authToken")
    if not token:
        return False

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return False

    return payload['id']


# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/support", methods=["POST"])
def support():
    name = request.form["name"]
    city = request.form["city"]
    email = request.form["email"]
    phone = request.form["phone"]
    text = request.form["text"]

    if not name or not city or not text:
        return {"status": "error", "message": "Заполните обязательные поля!"}
        
    
    db_helper.create_support_request(name, city, email, phone, text)

    return {"status": "ok"}


@app.route("/business")
def business():
    return render_template("business.html")

@app.route("/install-station-request", methods=["POST"])
def install_station_request():
    organization = request.form["organization"]
    city = request.form["city"]
    email = request.form["email"]
    phone = request.form["phone"]
    text = request.form["text"]

    if not organization or not city:
        return {"status": "error", "message": "Заполните обязательные поля!"}
        
    
    db_helper.create_install_station_request(organization, city, email, phone, text)

    return {"status": "ok"}



@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


# Авторизация (вход + регистрация)
@app.route("/auth")
def auth():
    if check_auth():
        return redirect("/station-map")
    return render_template("auth.html")


@app.route("/auth/start-flash-call", methods=["POST"])
def auth_start_flash_call():
    phone = phone_verification.clean_phone(request.form["phone"])
    phone_verification.verify_phone(phone)

    return {"status": "ok"}


@app.route("/auth/check-code", methods=["POST"])
def auth_check_code():
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
        
        resp = make_response({"status": "ok", "is_verified": True})
        resp.set_cookie('authToken', encoded_jwt, max_age=60*60*24*365*10)
        return resp
    elif res == 'incorrect':
        return {"status": "ok", "is_verified": False}
    elif res == 'attempts_exceeded':
        return {"status": "ok", "is_verified": False, "attempts_exceeded": True}
    elif res == 'timeout_exceeded':
        return {"status": "ok", "is_verified": False, "timeout_exceeded": True}


@app.route("/auth/vk-id")
def vk_id_auth():
    code = request.args.get("code")
    state = request.args.get("state")
    device_id = request.args.get("device_id")
    code_verifier = request.cookies.get("vkCodeVerifier")

    tokens = vk_id.exchange_code_for_tokens(code, state, device_id, code_verifier)
    access_token = tokens['access_token']
    user_info = vk_id.get_user_info(access_token)
    user_info = user_info['user']
    # print(user_info)
    phone = '+' + user_info['phone']

    user_id = db_helper.get_user_by_phone(phone)
    if not user_id:
        user_id = db_helper.create_raw_user(phone)
    else:
        user_id = user_id['id']

    current_user_data = db_helper.get_user(user_id)

    if 'name' in current_user_data and current_user_data['name']:
        name = current_user_data['name']
    else:
        name = user_info['first_name']
    
    if 'age' in current_user_data and current_user_data['age']:
        age = current_user_data['age']
    else:
        # there is only birthday (string) in the user_info
        age = datetime.datetime.now().year - int(user_info['birthday'][-4:])
    
    if 'gender' in current_user_data and current_user_data['gender']:
        gender = current_user_data['gender']
    else:
        if user_info['sex'] == 1:
            gender = 2
        elif user_info['sex'] == 2:
            gender = 1
        else:
            gender = 0
        

    db_helper.update_user_info(user_id, {'name': name, 'age': age, 'gender': gender})
    
    exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365*10)
    encoded_jwt = jwt.encode({"id": user_id, "exp": exp}, config.JWT_SECRET)
    if str(type(encoded_jwt)) == "<class 'bytes'>":
        encoded_jwt = encoded_jwt.decode()
    
    resp = make_response(redirect("/station-map"))
    resp.set_cookie('authToken', encoded_jwt, max_age=60*60*24*365*10)
    resp.set_cookie('vkCodeVerifier', '')
    return resp



@app.route("/logout")
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('authToken', '')
    return resp


# Аппараты на карте
@app.route("/station-map")
def station_map():
    return render_template("station_map.html")

@app.route("/station-map/get-stations")
def get_stations():
    return db_helper.get_stations()


@app.route("/station-map/take-umbrella", methods=["POST"])
def take_umbrella():
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


@app.route("/station-map/take-umbrella/success-payment", methods=["POST"])
def take_umbrella_success_payment():
    raw_data = request.get_data().decode()
    if not payments.is_notification_valid(request.headers.get('Content-HMAC'), raw_data):
        return {"code": 1}

    data = request.form
    # print(data.data)
    user_id = data.get("AccountId")
    # order_id = data.get("InvoiceId")
    currency = data.get("PaymentCurrency")
    amount = data.get("PaymentAmount")
    tx_id = data.get("TransactionId")
    token = data.get("Token")
    card_last_four = data.get("CardLastFour")
    custom_data = data.get("Data")
    payment_type = ""
    if custom_data:
        custom_data = json.loads(custom_data)
        # payment_mode = custom_data["paymentMode"]
        payment_type = custom_data["paymentType"]
        station_take = custom_data["stationTake"]

    if payment_type != "deposit":
        return {"code": 0}
    
    if currency != "RUB" or float(amount) != config.DEPOSIT_AMOUNT:
        print("Invalid payment")
        payments.refund_deposit_by_tx_id(tx_id)
        return {"code": 0}
    
    if not station_take and station_take != 0:
        print("Invalid station_take")
        payments.refund_deposit_by_tx_id(tx_id)
        return {"code": 0}
    
    real_active_order = db_helper.get_active_order(user_id)
    if real_active_order:
        print("Invalid order")
        payments.refund_deposit_by_tx_id(tx_id)
        return {"code": 0}
    
    order_id = db_helper.open_order(user_id, station_take)

    db_helper.update_user_payment_token(user_id, token)
    db_helper.update_user_payment_card_last_four(user_id, card_last_four)
    db_helper.set_order_deposit_tx_id(order_id, tx_id)
    
    # Манипуляции с аппаратной частью станции
    slot = station_controller.give_out_umbrella(order_id, station_take)
    if slot is None:
        db_helper.close_order(order_id, state=4)
        print("Failed to take an umbrella")
        return {"status": "error", "message": "Failed to take an umbrella"}
    
    db_helper.update_order_take_slot(order_id, slot)

    return {"code": 0}


@app.route("/station-map/take-umbrella/fail-payment", methods=["POST"])
def take_umbrella_fail_payment():
    print("take_umbrella_fail_payment")
    raw_data = request.get_data().decode()
    if not payments.is_notification_valid(request.headers.get('Content-HMAC'), raw_data):
        return {"code": 1}

    data = request.form
    user_id = data.get("AccountId")
    # order_id = data.get("InvoiceId")

    # real_active_order = db_helper.get_active_order(user_id)
    # if not real_active_order or real_active_order['id'] != int(order_id):
    #     return {"code": 1}
    
    # if real_active_order['deposit_tx_id']:
    #     return {"code": 1}
    
    #db_helper.close_order(order_id, state=3)
    db_helper.update_user_payment_token(user_id, None)
    db_helper.update_user_payment_card_last_four(user_id, None)

    return {"code": 0}


@app.route("/station-map/put-umbrella", methods=["POST"])
def put_umbrella():
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


@app.route("/station-map/get-order-status")
def get_order_status():
    user_id = check_auth()
    if not user_id:
        return redirect("/auth")
    
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
        if last_order['state'] == 0:
            order_status = "closed_successfully"
        elif last_order['state'] == 2:
            order_status = "timeout_exceeded"
        elif last_order['state'] == 3:
            order_status = "bank_error"
        else:
            order_status = "unknown"
        
        return {"status": "ok", "order_status": order_status}


@app.route('/profile')
def profile():
    if not check_auth():
        return redirect("/auth")
    return render_template("profile.html")

@app.route('/profile/get-user-info')
def profile_get_user_info():
    user_id = check_auth()
    if not user_id:
        return redirect("/auth")
    
    data = db_helper.get_user(user_id)
    res = {
        "id": data['id'],
        "phone": data['phone'],
        "name": data['name'],
        "gender": data['gender'],
        "age": data['age']
    }
    return res

@app.route('/profile/update-user-info', methods=['POST'])
def profile_update_user_info():
    user_id = check_auth()
    if not user_id:
        return redirect("/auth")
    
    data = request.get_json(force=True)
    db_helper.update_user_info(user_id, data)
    
    return {"status": "ok"}

@app.route("/profile/get-active-order")
def get_active_order():
    user_id = check_auth()
    if not user_id:
        return {"status": "ok", "order": None}

    order = db_helper.get_active_order(user_id)
    if not order:
        return {"status": "ok", "order": None}

    return {"status": "ok", "order": order}

@app.route("/profile/get-processed-orders")
def get_processed_orders():
    user_id = check_auth()
    if not user_id:
        return {"status": "ok", "orders": []}

    orders = db_helper.get_processed_orders(user_id)
    if not orders:
        return {"status": "ok", "orders": []}
    
    for i in range(len(orders)):
        orders[i]['station_take_address'] = db_helper.get_station(orders[i]['station_take'])['address']
        orders[i]['station_put_address'] = db_helper.get_station(orders[i]['station_put'])['address']

    return {"status": "ok", "orders": orders}



# Страница с бесконечной загрузкой, преднозначена для начальной страницы в station-map в навигаторе
@app.route("/loading")
def loading():
    return render_template("loading.html")


@app.route('/agreement')
def agreement():
    return send_from_directory(app.static_folder, "agreement.docx")


if __name__ == "__main__":
    if config.DEBUG:
        app.run(port=5000, debug=True, host=config.DEBUG_HOST, use_reloader=False)
    else:
        serve(app, host="0.0.0.0", port=5000, url_scheme="https", threads=100)
