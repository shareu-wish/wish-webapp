from flask import Flask
from flask import render_template

app = Flask(__name__)


# ознакомительная страничка С КОМПАНИЕЙ
@app.route('/')
def landing():
    return render_template("landing.html")


# ознакомительная страничка С СЕРВИСОМ
@app.route('/onboarding')
def onboarding():
    return render_template("onboarding.html")


# авторизация (номер телефона/сервисы)
@app.route('/auth')
def auth():
    return render_template("auth.html")


# проверка номера телефона со станицы авторизации
@app.route('/phone-check')
def phone_check():
    return render_template("phone_check.html")


# аппараты в формате карточек
'''@app.route('/devices-cards')
def devices_cards():
    return render_template("devises_cards.html")'''


# аппараты на карте (Яндекс-карты)
@app.route('/station-map')
def station_map():
    return render_template("station_map.html")


# ввод номера аппарата
@app.route('/device-code')
def device_code():
    return render_template("device_code.html")


# страница после оплаты депозита с номером ячейки зонта, фото и пожеланием
@app.route('/get')
def get_unbrella():
    return render_template("get_unbrella.html")


# страница после возвращения зонта с фото и ризывом возвращаться
@app.route('/insert')
def insert_umbrella():
    return render_template("insert_umbrella.html")


# личный кабинет пользователя с информацией о нём и статистикой
@app.route('/account')
def lk():
    return render_template("lk.html")


# личный кабинет пользователя с информацией о нём и статистикой
@app.route('/support')
def support():
    return render_template("support.html")


# служебная страничка на время разработки
@app.route('/development')
def development():
    return render_template("pass.html")


# служебная страничка на время разработки
@app.route('/test')
def test():
    return render_template("tests.html")


# Страница с бесконечной загрузкой, преднозначена для начальной страницы в station-map в навигаторе
@app.route('/loading')
def loading():
    return render_template("loading.html")


if __name__ == '__main__':
    app.run(port=8080, debug=True, host='192.168.10.104')