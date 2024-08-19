from flask import Flask, redirect, make_response, send_from_directory
from flask import render_template
import config
from waitress import serve
import phone_verification
from flask import request
import jwt
import datetime
import db_helper
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


@app.route("/business")
def business():
    return render_template("business.html")


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
    
    station_id = request.form["station_id"]

    can_take = db_helper.get_station(station_id)['can_take']
    if can_take <= 0:
        return {"status": "error", "message": "There are no umbrellas in this station"}
    
    if db_helper.get_active_order(user_id):
        return {"status": "error", "message": "You have an active order"}

    # Сложные манипуляции с банками...

    # Сложные манипуляции с аппаратной частью станции... (функция должна вернуть номер слота, который был открыт для пользователя)
    slot = 3

    order_id = db_helper.open_order(user_id, station_id, slot)

    return {"status": "ok", "slot": slot, "order_id": order_id}


@app.route("/station-map/put-umbrella", methods=["POST"])
def put_umbrella():
    user_id = check_auth()
    if not user_id:
        return {"status": "error", "message": "Unauthorized"}
    
    station_id = request.form["station_id"]

    can_put = db_helper.get_station(station_id)['can_put']
    if can_put <= 0:
        return {"status": "error", "message": "There are no empty slots in this station"}
    
    active_order = db_helper.get_active_order(user_id)
    if not active_order:
        return {"status": "error", "message": "You have no active orders"}
    order_id = active_order['id']

    # Сложные манипуляции с аппаратной частью станции... (функция должна вернуть номер слота, в который пользователь положил зонт)
    slot = 2

    # Сложные манипуляции с банками... Возврат залога

    db_helper.close_order(order_id, station_id, slot)

    return {"status": "ok", "order_id": order_id}



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
        app.run(port=5000, debug=True, host=config.DEBUG_HOST)
    else:
        serve(app, host="0.0.0.0", port=5000, url_scheme="https", threads=100)
