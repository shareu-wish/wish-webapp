from flask import Flask
from flask import render_template

application = Flask(__name__)


# ознакомительная страничка С КОМПАНИЕЙ
@application.route('/')
def landing():
    return render_template("landing.html")


# ознакомительная страничка С СЕРВИСОМ
@application.route('/onboarding')
def onboarding():
    return render_template("onboarding.html")


# авторизация (номер телефона/сервисы)
@application.route('/auth')
def auth():
    return render_template("auth.html")


# проверка номера телефона со станицы авторизации
@application.route('/phone_check')
def phone_check():
    return render_template("phone_check.html")


# аппараты в формате карточек
@application.route('/devices_cards')
def devices_cards():
    return render_template("devises_cards.html")


# аппараты на карте (Яндекс-карты)
@application.route('/devices_map')
def devices_map():
    return render_template("devises_map.html")


# ввод номера аппарата
@application.route('/device_code')
def device_code():
    return render_template("device_code.html")


# страница после оплаты депозита с номером ячейки зонта, фото и пожеланием
@application.route('/get')
def get_unbrella():
    return render_template("get_unbrella.html")


# страница после возвращения зонта с фото и ризывом возвращаться
@application.route('/insert')
def insert_umbrella():
    return render_template("insert_umbrella.html")


# личный кабинет пользователя с информацией о нём и статистикой
@application.route('/account')
def lk():
    return render_template("lk.html")


# личный кабинет пользователя с информацией о нём и статистикой
@application.route('/support')
def support():
    return render_template("support.html")


# служебная страничка на время разработки
@application.route('/development')
def development():
    return render_template("pass.html")


# служебная страничка на время разработки
@application.route('/test')
def test():
    return render_template("tests.html")


if __name__ == '__main__':
    application.run(port=8080, host='127.0.0.1')
