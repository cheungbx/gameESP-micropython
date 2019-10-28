from odroid_go import GO
import time

GO.lcd.set_font(GO.lcd.fonts.TT24)


def show_battery_voltage():
    GO.lcd.erase()
    GO.lcd.set_pos(0, 0)

    GO.lcd.print("Current Voltage: " + str(GO.battery.get_voltage()))


while True:
    show_battery_voltage()

    time.sleep(1)
