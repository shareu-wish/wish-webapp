import paho.mqtt.client as mqtt
import config
from threading import Timer
import db_helper


"""
wish
- station1
    - slot1
        - lock: (status: closed/opened, command: open/close)
        - has_umbrella: (status: y/n)
"""

stations_data = {}


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("wish/#")


def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    # wish/station2/slot17/lock
    topic_parts = msg.topic.split("/")
    print(topic_parts[1][:7])
    if topic_parts[1][:7] == "station" and topic_parts[2][4:] == "slot":
        station_id = int(topic_parts[1][7:])
        slot_id = int(topic_parts[2][4:])
        if station_id not in stations_data:
            stations_data[station_id] = {}
        if slot_id not in stations_data[station_id]:
            stations_data[station_id][slot_id] = {}
        stations_data[station_id][slot_id][topic_parts[3]] = msg.payload.decode()

    if topic_parts[1][:7] == "station":
        pass




def _init_station(station_id: int, slots_count: int) -> None:
    for slot_id in range(slots_count):
        mqttc.publish(f"wish/station{station_id}/slot{slot_id}/lock", "closed", qos=1, retain=True)
        mqttc.publish(f"wish/station{station_id}/slot{slot_id}/has_umbrella", "n", qos=1, retain=True)


def give_out_umbrella(station_id: int, success_func: callable, timeout_func: callable) -> int | None:
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

    db_helper

    return slot_with_umbrella


def put_umbrella(station_id: int) -> int | None:
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
    return free_slot
    




mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
mqttc.connect(config.MQTT_HOST, config.MQTT_PORT)

# mqttc.publish("wish/test1/z", "hey2", qos=1)

# _init_station(2, 20)

# mqttc.loop_start()

if __name__ == "__main__":
    # _init_station(2, 20)

    mqttc.loop_forever()
else:
    mqttc.loop_start()

