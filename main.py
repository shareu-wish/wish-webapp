from flask import Flask, redirect
from flask import render_template
import config
from waitress import serve
import phone_verification
from flask import request


app = Flask(__name__)


# Главная страница
@app.route('/')
def index():
    return render_template("index.html")


# Авторизация (вход + регистрация)
@app.route('/auth')
def auth():
    return render_template("auth.html")

@app.route('/auth/start-flash-call', methods=['POST'])
def auth_start_flash_call():
    phone = phone_verification.clean_phone(request.form['phone'])
    phone_verification.verify_phone(phone)

    return {"status": "ok"}

@app.route('/auth/check-code', methods=['POST'])
def auth_check_code():
    phone = phone_verification.clean_phone(request.form['phone'])
    pincode = request.form['code']
    res = phone_verification.submit_pincode(phone, pincode)

    return {"status": "ok", "is_verified": res}


# Аппараты на карте
@app.route('/station-map')
def station_map():
    return render_template("station_map.html")




# личный кабинет пользователя с информацией о нём и статистикой
# @app.route('/profile')
# def lk():
#     return render_template("lk.html")


# Страница с бесконечной загрузкой, преднозначена для начальной страницы в station-map в навигаторе
@app.route('/loading')
def loading():
    return render_template("loading.html")


if __name__ == '__main__':
    if config.DEBUG:
        app.run(port=5000, debug=True, host=config.DEBUG_HOST)
    else:
        serve(app, host='0.0.0.0', port=5000, url_scheme='https', threads=100)
