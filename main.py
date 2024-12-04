from flask import Flask, redirect, make_response, send_from_directory
from flask import render_template
import config
from waitress import serve
from flask import request
import requests


app = Flask(__name__)


def transform_auth():
    """
    Перенести authToken из cookies в Bearer Authorization header
    """
    token = request.cookies.get("authToken")
    if not token:
        return {}

    return {"Authorization": f"Bearer {token}"}


def check_auth():
    headers = transform_auth()
    response = requests.get(config.API_URL + "/v1/auth/check", headers=headers)
    if response.status_code == 200:
        return response.json().get("user_id")
    return False


def make_post_api_request(url: str, data):
    headers = transform_auth()
    return requests.post(config.API_URL + url, json=data, headers=headers).json()

def make_get_api_request(url: str):
    headers = transform_auth()
    return requests.get(config.API_URL + url, headers=headers).json()


# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/support", methods=["POST"])
def support():
    data = {}
    data['name'] = request.form['name']
    data['city'] = request.form['city']
    data['email'] = request.form['email']
    data['phone'] = request.form['phone']
    data['text'] = request.form['text']

    return make_post_api_request("/v1/landing-forms/support", data)


@app.route("/business")
def business():
    return render_template("business.html")

@app.route("/install-station-request", methods=["POST"])
def install_station_request():
    name = request.form["name"]
    organization = request.form["organization"]
    city = request.form["city"]
    email = request.form["email"]
    phone = request.form["phone"]
    text = request.form["text"]

    return make_post_api_request("/v1/landing-forms/install-station-request", {
        "name": name,
        "organization": organization,
        "city": city,
        "email": email,
        "phone": phone,
        "text": text
    })



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
    return make_post_api_request("/v1/auth/start-phone-verification", {"phone": request.form["phone"]})

@app.route("/auth/check-code", methods=["POST"])
def auth_check_code():
    res = make_post_api_request("/v1/auth/check-code", {
        "phone": request.form["phone"],
        "code": request.form["code"]
    })
    if res['is_verified']:
        resp = make_response({"status": "ok", "is_verified": True})
        resp.set_cookie('authToken', res['auth_token'], max_age=60*60*24*365*10)
        return resp
    return {"status": "ok", "is_verified": False}


# @app.route("/auth/vk-id")
# def vk_id_auth():
#     code = request.args.get("code")
#     state = request.args.get("state")
#     device_id = request.args.get("device_id")
#     code_verifier = request.cookies.get("vkCodeVerifier")

#     tokens = vk_id.exchange_code_for_tokens(code, state, device_id, code_verifier)
#     access_token = tokens['access_token']
#     user_info = vk_id.get_user_info(access_token)
#     user_info = user_info['user']
#     # print(user_info)
#     phone = '+' + user_info['phone']

#     user_id = db_helper.get_user_by_phone(phone)
#     if not user_id:
#         user_id = db_helper.create_raw_user(phone)
#     else:
#         user_id = user_id['id']

#     current_user_data = db_helper.get_user(user_id)

#     if 'name' in current_user_data and current_user_data['name']:
#         name = current_user_data['name']
#     else:
#         name = user_info['first_name']
    
#     if 'age' in current_user_data and current_user_data['age']:
#         age = current_user_data['age']
#     else:
#         # there is only birthday (string) in the user_info
#         age = datetime.datetime.now().year - int(user_info['birthday'][-4:])
    
#     if 'gender' in current_user_data and current_user_data['gender']:
#         gender = current_user_data['gender']
#     else:
#         if user_info['sex'] == 1:
#             gender = 2
#         elif user_info['sex'] == 2:
#             gender = 1
#         else:
#             gender = 0
        

#     db_helper.update_user_info(user_id, {'name': name, 'age': age, 'gender': gender})
    
#     exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365*10)
#     encoded_jwt = jwt.encode({"id": user_id, "exp": exp}, config.JWT_SECRET)
#     if str(type(encoded_jwt)) == "<class 'bytes'>":
#         encoded_jwt = encoded_jwt.decode()
    
#     resp = make_response(redirect("/station-map"))
#     resp.set_cookie('authToken', encoded_jwt, max_age=60*60*24*365*10)
#     resp.set_cookie('vkCodeVerifier', '')
#     return resp



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
    return make_get_api_request("/v1/stations/get-all-stations")

@app.route("/station-map/take-umbrella", methods=["POST"])
def take_umbrella():
    return make_post_api_request("/v1/orders/take-umbrella", {
        "station_take": request.form["station_id"]
    })

@app.route("/station-map/put-umbrella", methods=["POST"])
def put_umbrella():
    return make_post_api_request("/v1/orders/put-umbrella", {
        "station_put": request.form["station_id"]
    })

@app.route("/station-map/get-order-status")
def get_order_status():
    return make_get_api_request("/v1/orders/get-order-status")


# Feedback
@app.route("/station-map/order-feedback", methods=["POST"])
def order_feedback():
    data = request.get_json(force=True)
    return make_post_api_request("/v1/orders/order-feedback", data)


# Profile
@app.route('/profile')
def profile():
    if not check_auth():
        return redirect("/auth")
    return render_template("profile.html")

@app.route('/profile/get-user-info')
def profile_get_user_info():
    return make_get_api_request("/v1/profile/get-user-info")

@app.route('/profile/update-user-info', methods=['POST'])
def profile_update_user_info():
    data = request.get_json(force=True)
    return make_post_api_request("/v1/profile/update-user-info", data)

@app.route('/profile/get-subscription-info')
def profile_get_subscription_info():
    return make_get_api_request("/v1/subscription/get-subscription-info")

@app.route("/profile/get-active-order")
def get_active_order():
    return make_get_api_request("/v1/orders/get-active-order")

@app.route("/profile/get-processed-orders")
def get_processed_orders():
    return make_get_api_request("/v1/orders/get-processed-orders")



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
