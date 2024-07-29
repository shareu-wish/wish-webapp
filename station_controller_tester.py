import station_controller
import time


station_id = 2

time.sleep(1)
# Выдать зонт
slot = station_controller.give_out_umbrella(station_id)
print(slot)

print(type(station_controller.give_out_umbrella))