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


def get_user(id: int):
    """
    Получить запись из таблицы users
    :param id: ID пользователя
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


def get_user_by_phone(phone: str):
    """
    Получить запись из таблицы users
    :param phone: Номер телефона
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


if not config.DEBUG:
    _schedule_delete_old_data()


if __name__ == "__main__":
    # create_verify_phone_record("1234567890", "1234")
    # print(get_verify_phone_record("1234567890"))
    # delete_verify_phone_record("1234567890")
    print(get_user_by_phone('453'))
