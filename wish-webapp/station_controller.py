import paho.mqtt.client as mqtt
import config
from threading import Timer
import db_helper
from time import sleep
import payments


"""
wish
- station1
    - slot1
        - lock: (status: closed/opened, command: open/close)
        - has_umbrella: (status: y/n)
"""

stations_data = {}


def _monitor_take_umbrella_timeout():
    Timer(2, _monitor_take_umbrella_timeout).start()
    timeouts = db_helper.get_all_station_lock_timeouts()

    for timeout in timeouts:
        if timeout['type'] == 1:
            # Вернуть депозит пользователю
            try:
                payments.refund_deposit(db_helper.get_order(timeout['order_id'])['user_id'])
                print("Отзываем депозит из-за таймаута, user_id:", db_helper.get_order(timeout['order_id'])['user_id'])
            except Exception as e:
                print("timeout: refund_deposit:")
                print(e)
            
            mqttc.publish(f"wish/station{timeout['station_id']}/slot{timeout['slot']}/lock", "close", qos=1, retain=True)
            db_helper.close_order(timeout['order_id'], state=2)
            db_helper.delete_station_lock_timeout(timeout['id'])
        elif timeout['type'] == 2:
            mqttc.publish(f"wish/station{timeout['station_id']}/slot{timeout['slot']}/lock", "close", qos=1, retain=True)
            db_helper.delete_station_lock_timeout(timeout['id'])




def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("wish/#")


def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    # wish/station2/slot17/lock
    topic_parts = msg.topic.split("/")
    # print(topic_parts[1][:7])
    if topic_parts[1][:7] == "station" and topic_parts[2][:4] == "slot" and topic_parts[3]:
        station_id = int(topic_parts[1][7:])
        slot_id = int(topic_parts[2][4:])
        if station_id not in stations_data:
            stations_data[station_id] = {}
        if slot_id not in stations_data[station_id]:
            stations_data[station_id][slot_id] = {}
        stations_data[station_id][slot_id][topic_parts[3]] = msg.payload.decode()

        if topic_parts[3] == "has_umbrella" and msg.payload.decode() == "n":
            timeout = db_helper.get_station_lock_timeout_by_station_and_slot(station_id, slot_id)
            if timeout is not None:
                db_helper.decrease_free_umbrellas_on_station(station_id)
                db_helper.delete_station_lock_timeout(timeout['id'])
                sleep(2)
                mqttc.publish(f"wish/station{station_id}/slot{slot_id}/lock", "close", qos=1, retain=True)
        elif topic_parts[3] == "has_umbrella" and msg.payload.decode() == "y":
            timeout = db_helper.get_station_lock_timeout_by_station_and_slot(station_id, slot_id)
            if timeout is not None:
                db_helper.increase_free_umbrellas_on_station(station_id)
                db_helper.delete_station_lock_timeout(timeout['id'])
                # sleep(0.5)
                mqttc.publish(f"wish/station{station_id}/slot{slot_id}/lock", "close", qos=1, retain=True)

                # Вернуть депозит
                payments.refund_deposit(db_helper.get_order(timeout['order_id'])['user_id'])
                print("Возвращаем депозит, user_id:", db_helper.get_order(timeout['order_id'])['user_id'])

                db_helper.close_order(timeout['order_id'], station_id, slot_id)




def _init_station(station_id: int, slots_count: int) -> None:
    for slot_id in range(slots_count):
        mqttc.publish(f"wish/station{station_id}/slot{slot_id}/lock", "closed", qos=1, retain=True)
        mqttc.publish(f"wish/station{station_id}/slot{slot_id}/has_umbrella", "n", qos=1, retain=True)


def give_out_umbrella(order_id: int, station_id: int) -> int | None:
    """
    Выдать зонт пользователю

    :param order_id: id заказа
    :param station_id: id станции
    :return: id слота, который был открыт
    """
    if station_id not in stations_data:
        return None
    
    slot_with_umbrella = None
    for slot_id, slot_data in stations_data[station_id].items():
        if slot_data['lock'] == 'closed' and slot_data['has_umbrella'] == 'y':
            slot_with_umbrella = slot_id
            break
    
    if slot_with_umbrella is None:
        return None
    
    mqttc.publish(f"wish/station{station_id}/slot{slot_with_umbrella}/lock", "open", qos=1, retain=True)

    db_helper.set_station_take_umbrella_timeout(order_id, station_id, slot_with_umbrella)

    return slot_with_umbrella


def put_umbrella(order_id: int, station_id: int) -> int | None:
    """
    Открыть ячейку для возврата зонта

    :param order_id: id заказа
    :param station_id:
    :return: id слота, который был открыт
    """
    if station_id not in stations_data:
        return None
    
    free_slot = None
    for slot_id, slot_data in stations_data[station_id].items():
        if slot_data['lock'] == 'closed' and slot_data['has_umbrella'] == 'n':
            free_slot = slot_id
            break
    
    if free_slot is None:
        return None
    
    mqttc.publish(f"wish/station{station_id}/slot{free_slot}/lock", "open", qos=1, retain=True)

    db_helper.set_station_put_umbrella_timeout(order_id, station_id, free_slot)

    return free_slot
    




mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
mqttc.connect(config.MQTT_HOST, config.MQTT_PORT)

# mqttc.publish("wish/test1/z", "hey2", qos=1)

# _init_station(2, 20)

# mqttc.loop_start()

# if not config.DEBUG:
_monitor_take_umbrella_timeout()


if __name__ == "__main__":
    # _init_station(2, 20)

    mqttc.loop_forever()
else:
    mqttc.loop_start()

