from flask import Flask, redirect, make_response
from flask import render_template
import config
from waitress import serve
import phone_verification
from flask import request
import jwt
import datetime
import db_helper


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

        user_id = user_id['id']
        exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365*10)
        encoded_jwt = jwt.encode({"id": user_id, "exp": exp}, config.JWT_SECRET)
        encoded_jwt = encoded_jwt.decode()
        
        resp = make_response({"status": "ok", "is_verified": True})
        resp.set_cookie('authToken', encoded_jwt)
        return resp
    elif res == 'incorrect':
        return {"status": "ok", "is_verified": False}
    elif res == 'attempts_exceeded':
        return {"status": "ok", "is_verified": False, "attempts_exceeded": True}
    elif res == 'timeout_exceeded':
        return {"status": "ok", "is_verified": False, "timeout_exceeded": True}


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


@app.route('/profile')
def profile():
    print(check_auth())
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




# Страница с бесконечной загрузкой, преднозначена для начальной страницы в station-map в навигаторе
@app.route("/loading")
def loading():
    return render_template("loading.html")


if __name__ == "__main__":
    if config.DEBUG:
        app.run(port=5000, debug=True, host=config.DEBUG_HOST)
    else:
        serve(app, host="0.0.0.0", port=5000, url_scheme="https", threads=100)
