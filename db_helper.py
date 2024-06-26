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


def delete_verify_phone_record(phone: str) -> None:
    """
    Удалить запись из таблицы user_verification
    :param phone: Номер телефона
    """

    cur = conn.cursor()
    cur.execute("DELETE FROM user_verification WHERE phone = %s", (phone, ))
    conn.commit()
    cur.close()


def create_raw_user(phone: str) -> None:
    """
    Создать запись в таблице users
    :param phone: Номер телефона
    """

    cur = conn.cursor()
    cur.execute("INSERT INTO users (phone) VALUES (%s)", (phone,))
    conn.commit()
    cur.close()


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


_schedule_delete_old_data()

if __name__ == "__main__":
    create_verify_phone_record("1234567890", "1234")
    print(get_verify_phone_record("1234567890"))
    delete_verify_phone_record("1234567890")
