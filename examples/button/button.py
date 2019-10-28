from odroid_go import GO
import time

GO.lcd.set_font(GO.lcd.fonts.TT14)


def display_buttons():
    GO.lcd.erase()
    GO.lcd.set_pos(0, 0)

    GO.lcd.print("/* Direction Pad */")
    GO.lcd.print("Joy-Y-Up: " + ("Pressed" if GO.btn_joy_y.is_axis_pressed() == 2 else ""))
    GO.lcd.print("Joy-Y-Down: " + ("Pressed" if GO.btn_joy_y.is_axis_pressed() == 1 else ""))
    GO.lcd.print("Joy-X-Left: " + ("Pressed" if GO.btn_joy_x.is_axis_pressed() == 2 else ""))
    GO.lcd.print("Joy-X-Right: " + ("Pressed" if GO.btn_joy_x.is_axis_pressed() == 1 else ""))
    GO.lcd.print("")
    GO.lcd.print("/* Function Key */")
    GO.lcd.print("Menu: " + ("Pressed" if GO.btn_menu.is_pressed() == 1 else ""))
    GO.lcd.print("Volume: " + ("Pressed" if GO.btn_volume.is_pressed() == 1 else ""))
    GO.lcd.print("Select: " + ("Pressed" if GO.btn_select.is_pressed() == 1 else ""))
    GO.lcd.print("Start: " + ("Pressed" if GO.btn_start.is_pressed() == 1 else ""))
    GO.lcd.print("")
    GO.lcd.print("/* Actions */")
    GO.lcd.print("B: " + ("Pressed" if GO.btn_b.is_pressed() == 1 else ""))
    GO.lcd.print("A: " + ("Pressed" if GO.btn_a.is_pressed() == 1 else ""))


while True:
    GO.update()
    display_buttons()

    time.sleep(1)
