from flask import Blueprint
import config
import jwt
from flask import request
import db_helper
import phone_verification
import datetime


api_v1 = Blueprint('api_v1', __name__)


def check_auth():
    """
    Проверка авторизации
    """
    token = request.cookies.get("authToken")
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
