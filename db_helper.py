import psycopg2
import config
from threading import Timer


conn = psycopg2.connect(
    dbname=config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
)


def create_verify_phone_record(phone: str, pincode: str) -> None:
    """
    Создать запись в таблице user_verification

    :param phone: Номер телефона
    :param pincode: Пинкод
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO user_verification (phone, pincode) VALUES (%s, %s)", (phone, pincode))
    conn.commit()
    cur.close()


def get_verify_phone_record(phone: str) -> tuple[str]:
    """
    Получить запись из таблицы user_verification

    :param phone: Номер телефона
    :return: tuple (phone, pincode)
    """

    cur = conn.cursor()
    cur.execute("SELECT phone, pincode FROM user_verification WHERE phone = %s", (phone,))
    result = cur.fetchone()
    cur.close()

    return result


def update_verify_phone_record(phone: str, pincode: str) -> None:
    """
    Обновить запись в таблице user_verification

    :param phone: Номер телефона
    :param pincode: Пинкод
    """

    cur = conn.cursor()
    cur.execute("UPDATE user_verification SET pincode = %s, attempts = 0 WHERE phone = %s", (pincode, phone))
    conn.commit()
    cur.close()


def delete_verify_phone_record(phone: str) -> None:
    """
    Удалить запись из таблицы user_verification

    :param phone: Номер телефона
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM user_verification WHERE phone = %s", (phone, ))
    conn.commit()
    cur.close()


def create_raw_user(phone: str) -> int:
    """
    Создать запись в таблице users

    :param phone: Номер телефона
    :return: ID пользователя
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO users (phone) VALUES (%s)", (phone,))
    conn.commit()
    cur.close()

    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE phone = %s", (phone,))
    user_id = cur.fetchone()[0]
    cur.close()

    return user_id


def increment_attempts(phone: str) -> int:
    """
    Увеличить количество попыток в таблице user_verification

    :param phone: Номер телефона
    :return: Количество попыток
    """

    cur = conn.cursor()
    cur.execute("UPDATE user_verification SET attempts = attempts + 1 WHERE phone = %s", (phone,))
    conn.commit()
    cur.close()

    cur = conn.cursor()
    cur.execute("SELECT attempts FROM user_verification WHERE phone = %s", (phone,))
    attempts = cur.fetchone()[0]
    cur.close()
    
    return attempts


def _delete_old_data() -> None:
    """
    Удалить старые записи из таблицы user_verification
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM user_verification WHERE created_at < NOW() - INTERVAL '10 minute'")
    conn.commit()
    cur.close()


def _schedule_delete_old_data() -> None:
    """
    Запланировать удаление старых записей
    """
    _delete_old_data()
    Timer(60*2, _schedule_delete_old_data).start()


def get_user(id: int) -> dict:
    """
    Получить запись из таблицы users

    :param id: ID пользователя
    :return: Словарь с данными пользователя\n
        - *id*: ID пользователя
        - *phone*: Номер телефона
        - *name*: Имя
        - *gender*: Пол
        - *age*: Возраст
    """

    cur = conn.cursor()
    cur.execute("SELECT id, phone, name, gender, age FROM users WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    res = {
        "id": data[0],
        "phone": data[1],
        "name": data[2],
        "gender": data[3],
        "age": data[4]
    }

    return res


def get_user_by_phone(phone: str) -> dict | None:
    """
    Получить запись из таблицы users

    :param phone: Номер телефона
    :return: Словарь с данными пользователя или None, если пользователь не найден\n
        - *id*: ID пользователя
        - *phone*: Номер телефона
        - *name*: Имя
        - *gender*: Пол
        - *age*: Возраст
    """

    cur = conn.cursor()
    cur.execute("SELECT id, phone, name, gender, age FROM users WHERE phone = %s", (phone, ))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "phone": data[1],
        "name": data[2],
        "gender": data[3],
        "age": data[4]
    }

    return res


def update_user_info(id: int, data: dict) -> None:
    """
    Обновить запись в таблице users

    :param id: ID пользователя
    :param data: Данные пользователя (name, gender, age)
    """

    cur = conn.cursor()
    cur.execute("UPDATE users SET name = %s, gender = %s, age = %s WHERE id = %s", (data["name"], data["gender"], data["age"], id))
    conn.commit()
    cur.close()


def get_stations() -> list[dict]:
    """
    Получить все записи из таблицы stations

    :return: Список станций
    """

    cur = conn.cursor()
    cur.execute("SELECT id, title, address, latitude, longitude, opening_hours, capacity, can_put, can_take, picture, information, state FROM stations")
    data = cur.fetchall()
    cur.close()

    res = []
    for station in data:
        res.append({
            "id": station[0],
            "title": station[1],
            "address": station[2],
            "latitude": station[3],
            "longitude": station[4],
            "opening_hours": station[5],
            "capacity": station[6],
            "can_put": station[7],
            "can_take": station[8],
            "picture": station[9],
            "information": station[10],
            "state": station[11]
        })

    return res


def get_station(id: int) -> dict:
    """
    Получить запись из таблицы stations

    :param id: ID станции
    """

    cur = conn.cursor()
    cur.execute("SELECT id, title, address, latitude, longitude, opening_hours, capacity, can_put, can_take, picture, information, state FROM stations WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    res = {
        "id": data[0],
        "title": data[1],
        "address": data[2],
        "latitude": data[3],
        "longitude": data[4],
        "opening_hours": data[5],
        "capacity": data[6],
        "can_put": data[7],
        "can_take": data[8],
        "picture": data[9],
        "information": data[10],
        "state": data[11]
    }

    return res


def open_order(user_id: int, station_id: int, slot: int) -> int:
    """
    Создать запись в таблице orders

    :param user_id: ID пользователя
    :param station_id: ID станции
    :param slot: номер слота на станции
    :return: ID заказа
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, state, station_take, slot_take) VALUES (%s, %s, %s, %s) RETURNING id", (user_id, 1, station_id, slot))
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    return order_id


def get_active_order(user_id: int) -> dict:
    """
    Получить активный заказ пользователя

    :param user_id: ID пользователя
    :return: dict с данными о заказе
    """

    cur = conn.cursor()
    cur.execute("SELECT id, state, datetime_take, station_take, slot_take FROM orders WHERE user_id = %s AND state = 1", (user_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "state": data[1],
        "datetime_take": data[2],
        "station_take": data[3],
        "slot_take": data[4]
    }

    return res


def close_order(order_id: int, station_id: int, slot: int) -> None:
    """
    Закрыть заказ пользователя

    :param order_id: ID заказа
    :param station_id: ID станции, в которую был помещен зонт
    :param slot: номер слота на станции, куда был помещен зонт
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET state = 0, station_put = %s, slot_put = %s, datetime_put = now() WHERE id = %s", (station_id, slot, order_id))
    conn.commit()
    cur.close()


def get_processed_orders(user_id: int) -> dict:
    """
    Получить все обработанные заказы пользователя

    :param user_id: ID пользователя
    :return: Список заказов
    """

    cur = conn.cursor()
    cur.execute("SELECT id, state, datetime_take, datetime_put, station_take, station_put, slot_take, slot_put FROM orders WHERE user_id = %s AND state = 0", (user_id, ))
    data = cur.fetchall()
    cur.close()

    res = []
    for order in data:
        res.append({
            "id": order[0],
            "state": order[1],
            "datetime_take": order[2],
            "datetime_put": order[3],
            "station_take": order[4],
            "station_put": order[5],
            "slot_take": order[6],
            "slot_put": order[7]
        })

    return res


def create_support_request(name: str, city: str, email: str, phone: str, text: str) -> None:
    """
    Создать запись в таблице поддержки

    :param name: Имя
    :param city: Город
    :param email: Email
    :param phone: Номер телефона
    :param text: Текст обращения
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO support (name, city, email, phone, text) VALUES (%s, %s, %s, %s, %s)", (name, city, email, phone, text))
    conn.commit()
    cur.close()


def create_install_station_request(name: str, organization: str, city: str, email: str, phone: str, text: str) -> None:
    """
    Создать запись в таблице с заявками на установку станции

    :param name: Имя того, кто оставляет заявку
    :param organization: Название организации
    :param city: Город
    :param email: Email
    :param phone: Номер телефона
    :param text: Комментарий
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO install_station_requests (name, organization, city, email, phone, text) VALUES (%s, %s, %s, %s, %s, %s)", (name, organization, city, email, phone, text))
    conn.commit()
    cur.close()



if not config.DEBUG:
    _schedule_delete_old_data()


if __name__ == "__main__":
    # create_verify_phone_record("1234567890", "1234")
    # print(get_verify_phone_record("1234567890"))
    # delete_verify_phone_record("1234567890")
    print(get_active_order(9))
