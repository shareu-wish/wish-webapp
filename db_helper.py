import psycopg2
import config
from threading import Timer
from datetime import datetime



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
    cur.execute("DELETE FROM user_verification WHERE created_at < %s - INTERVAL '10 minute'", (datetime.now(),))
    conn.commit()
    cur.close()


def _schedule_delete_old_data() -> None:
    """
    Запланировать удаление старых записей
    """
    _delete_old_data()
    Timer(60*2, _schedule_delete_old_data).start()


""" User """
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
        - *payment_card_last_four*: Последние 4 цифры платежной карты
    """

    cur = conn.cursor()
    cur.execute("SELECT id, phone, name, gender, age, payment_card_last_four, FROM users WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    res = {
        "id": data[0],
        "phone": data[1],
        "name": data[2],
        "gender": data[3],
        "age": data[4],
        "payment_card_last_four": data[5]
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
        - *payment_card_last_four*: Последние 4 цифры платежной карты
    """

    cur = conn.cursor()
    cur.execute("SELECT id, phone, name, gender, age, payment_card_last_four FROM users WHERE phone = %s", (phone, ))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "phone": data[1],
        "name": data[2],
        "gender": data[3],
        "age": data[4],
        "payment_card_last_four": data[5]
    }

    return res


def update_user_info(id: int, data: dict) -> None:
    """
    Обновить имя, пол, возраст пользователя

    :param id: ID пользователя
    :param data: Данные пользователя (name, gender, age)
    """

    cur = conn.cursor()
    cur.execute("UPDATE users SET name = %s, gender = %s, age = %s WHERE id = %s", (data["name"], data["gender"], data["age"], id))
    conn.commit()
    cur.close()


def get_user_payment_token(id: int) -> str:
    """
    Получить токен платежа пользователя

    :param id: ID пользователя
    :return: Токен платежа
    """

    cur = conn.cursor()
    cur.execute("SELECT payment_token FROM users WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    return data[0]


def update_user_payment_token(id: int, token: str) -> None:
    """
    Обновить токен платежа пользователя

    :param id: ID пользователя
    :param token: Токен платежа
    """

    cur = conn.cursor()
    cur.execute("UPDATE users SET payment_token = %s WHERE id = %s", (token, id))
    conn.commit()
    cur.close()


def update_user_payment_card_last_four(id: int, last_four: str) -> None:
    """
    Обновить последние 4 цифры платежной карты пользователя

    :param id: ID пользователя
    :param last_four: Последние 4 цифры платежной карты
    """

    cur = conn.cursor()
    cur.execute("UPDATE users SET payment_card_last_four = %s WHERE id = %s", (last_four, id))
    conn.commit()
    cur.close()



""" Stations """
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


def decrease_free_umbrellas_on_station(station_id: int) -> None:
    """
    Уменьшить количество свободных зонтов на станции

    :param station_id: ID станции
    """
    
    print("decrease_free_umbrellas_on_station")
    cur = conn.cursor()
    cur.execute("UPDATE stations SET can_take = can_take - 1 WHERE id = %s", (station_id,))
    cur.execute("UPDATE stations SET can_put = can_put + 1 WHERE id = %s", (station_id,))
    conn.commit()
    cur.close()


def increase_free_umbrellas_on_station(station_id: int) -> None:
    """
    Увеличить количество свободных зонтов на станции

    :param station_id: ID станции
    """

    print("increase_free_umbrellas_on_station")
    cur = conn.cursor()
    cur.execute("UPDATE stations SET can_take = can_take + 1 WHERE id = %s", (station_id,))
    cur.execute("UPDATE stations SET can_put = can_put - 1 WHERE id = %s", (station_id,))
    conn.commit()
    cur.close()


""" Orders """
def open_order(user_id: int, station_id: int, slot: int = None) -> int:
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


def get_active_order(user_id: int) -> dict | None:
    """
    Получить активный заказ пользователя

    :param user_id: ID пользователя
    :return: dict с данными о заказе\n
        - *id*: ID заказа
        - *state*: Статус заказа
        - *datetime_take*: Дата и время взятия зонтов
        - *station_take*: ID станции, в которую был помещен зонт
        - *slot_take*: номер слота на станции, куда был помещен зонт
        - *deposit_tx_id*: ID транзакции, в которой был сделан депозит
    """

    cur = conn.cursor()
    cur.execute("SELECT id, state, datetime_take, station_take, slot_take, deposit_tx_id FROM orders WHERE user_id = %s AND state = 1", (user_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "state": data[1],
        "datetime_take": data[2],
        "station_take": data[3],
        "slot_take": data[4],
        "deposit_tx_id": data[5]
    }

    return res


def close_order(order_id: int, station_id: int = None, slot: int = None, state: int = 0) -> None:
    """
    Закрыть заказ пользователя

    :param order_id: ID заказа
    :param station_id: ID станции, в которую был помещен зонт
    :param slot: номер слота на станции, куда был помещен зонт
    :param state: Статус заказа\n
        + **0** - заказ закрыт (стандартно)
        + **1** - заказ открыт
        + **2** - заказ закрыт т. к. пользователь не взял зонт вовремя
        + **3** - заказ закрыт из-за проблем с оплатой
        + **4** - заказ закрыт из-за внутренней ошибки (например, нет свободных зонтов)
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET state = %s, station_put = %s, slot_put = %s, datetime_put = %s WHERE id = %s", (state, station_id, slot, datetime.now(), order_id))
    conn.commit()
    cur.close()


def get_processed_orders(user_id: int) -> list[dict]:
    """
    Получить все обработанные заказы пользователя

    :param user_id: ID пользователя
    :return: Список заказов\n
        - *id*: ID заказа
        - *state*: Статус заказа
        - *datetime_take*: Дата и время взятия зонтов
        - *datetime_put*: Дата и время возврата зонтов
        - *station_take*: ID станции, в которую был помещен зонт
        - *station_put*: ID станции, из которой был взят зонт
        - *slot_take*: номер слота на станции, куда был помещен зонт
        - *slot_put*: номер слота на станции, из которой был взят зонт
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


def update_order_take_slot(order_id: int, slot: int) -> None:
    """
    Обновить запись в таблице orders

    :param order_id: ID заказа
    :param slot: номер слота на станции, куда был помещен зонт
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET slot_take = %s WHERE id = %s", (slot, order_id))
    conn.commit()
    cur.close()


def set_order_deposit_tx_id(order_id: int, tx_id: int) -> None:
    """
    Установить ID транзакции депозита для заказа

    :param order_id: ID заказа
    :param tx_id: ID транзакции, в которой был сделан депозит
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET deposit_tx_id = %s WHERE id = %s", (tx_id, order_id))
    conn.commit()
    cur.close()


def get_last_order(user_id: int) -> dict | None:
    """
    Получить последний заказ пользователя

    :param user_id: ID пользователя
    :return: dict с данными о заказе\n
        - *id*: ID заказа
        - *state*: Статус заказа
        - *datetime_take*: Дата и время взятия зонтов
        - *datetime_put*: Дата и время возврата зонтов
        - *station_take*: ID станции, в которую был помещен зонт
        - *station_put*: ID станции, из которой был взят зонт
        - *slot_take*: номер слота на станции, куда был помещен зонт
        - *slot_put*: номер слота на станции, из которой был взят зонт
    """

    cur = conn.cursor()
    cur.execute("SELECT id, state, datetime_take, datetime_put, station_take, station_put, slot_take, slot_put FROM orders WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None
    
    res = {
        "id": data[0],
        "state": data[1],
        "datetime_take": data[2],
        "datetime_put": data[3],
        "station_take": data[4],
        "station_put": data[5],
        "slot_take": data[6],
        "slot_put": data[7]
    }
    return res


def set_order_deposit_tx_id(order_id: int, tx_id: str) -> None:
    """
    Установить ID транзакции для заказа

    :param order_id: ID заказа
    :param tx_id: ID транзакции
    """

    cur = conn.cursor()
    cur.execute("UPDATE orders SET deposit_tx_id = %s WHERE id = %s", (tx_id, order_id))
    conn.commit()
    cur.close()


""" Station controller """
TIME_TO_TAKE_UMBRELLA = config.TIME_TO_TAKE_UMBRELLA


def set_station_take_umbrella_timeout(order_id: int, station_id: int, slot_id: int) -> None:
    """
    Установить таймаут для взятия зонта

    :param order_id: ID заказа
    :param station_id: ID станции
    :param slot_id: ID слота
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO station_lock_timeouts (order_id, station_id, slot, datetime_opened, type) VALUES (%s, %s, %s, %s, %s)", (order_id, station_id, slot_id, datetime.now(), 1))
    conn.commit()
    cur.close()


def set_station_put_umbrella_timeout(order_id: int, station_id: int, slot_id: int) -> None:
    """
    Установить таймаут для возврата зонта

    :param order_id: ID заказа
    :param station_id: ID станции
    :param slot_id: ID слота
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO station_lock_timeouts (order_id, station_id, slot, datetime_opened, type) VALUES (%s, %s, %s, %s, %s)", (order_id, station_id, slot_id, datetime.now(), 2))
    conn.commit()
    cur.close()


def get_all_station_lock_timeouts() -> list[dict]:
    """
    Найти таймауты для открытия станций

    :return: Список таймаутов
    """

    cur = conn.cursor()
    cur.execute("SELECT id, order_id, station_id, slot, datetime_opened, type FROM station_lock_timeouts WHERE datetime_opened + interval '%s second' < %s", (TIME_TO_TAKE_UMBRELLA, datetime.now()))
    data = cur.fetchall()
    cur.close()

    res = []
    for timeout in data:
        res.append({
            "id": timeout[0],
            "order_id": timeout[1],
            "station_id": timeout[2],
            "slot": timeout[3],
            "datetime_opened": timeout[4],
            "type": timeout[5]
        })

    return res


def get_station_lock_timeout_by_order_id(order_id: int) -> dict | None:
    """
    Найти таймаут открытия станции

    :param order_id: ID заказа
    :return: dict с данными о таймауте\n
        - *id*: ID таймаута
        - *station_id*: ID станции
        - *slot*: ID слота
        - *datetime_opened*: Дата и время открытия
        - *type*: Тип таймаута (1 - взятие зонта, 2 - возврат зонта)
    """

    cur = conn.cursor()
    cur.execute("SELECT id, station_id, slot, datetime_opened, type FROM station_lock_timeouts WHERE order_id = %s", (order_id,))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "station_id": data[1],
        "slot": data[2],
        "datetime_opened": data[3],
        "type": data[4]
    }

    return res


def get_station_lock_timeout_by_station_and_slot(station_id: int, slot: int) -> dict | None:
    """
    Найти таймаут открытия станции

    :param station_id: ID станции
    :param slot: ID слота
    :return: dict с данными о таймауте\n
        - *id*: ID таймаута
        - *order_id*: ID заказа
        - *datetime_opened*: Дата и время открытия
        - *type*: Тип таймаута (1 - взятие зонта, 2 - возврат зонта)
    """

    cur = conn.cursor()
    cur.execute("SELECT id, order_id, datetime_opened, type FROM station_lock_timeouts WHERE station_id = %s AND slot = %s", (station_id, slot))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    res = {
        "id": data[0],
        "order_id": data[1],
        "datetime_opened": data[2],
        "type": data[3]
    }

    return res


def delete_station_lock_timeout(id: int) -> None:
    """
    Удалить таймаут открытия станции

    :param id: ID таймаута
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM station_lock_timeouts WHERE id = %s", (id,))
    conn.commit()
    cur.close()


""" Payment """
def get_user_payment_token(user_id: int) -> str | None:
    """
    Получить токен оплаты пользователя

    :param user_id: ID пользователя
    :return: Токен оплаты
    """

    cur = conn.cursor()
    cur.execute("SELECT payment_token FROM users WHERE id = %s", (user_id, ))
    data = cur.fetchone()
    cur.close()

    if data is None:
        return None

    return data[0]


if not config.DEBUG:
    _schedule_delete_old_data()


if __name__ == "__main__":
    print(get_all_station_lock_timeouts())
