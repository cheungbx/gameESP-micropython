from odroid_go import GO

GO.lcd.set_font(GO.lcd.fonts.TT24)
GO.lcd.print("ODROID-GO speaker test:")

GO.speaker.set_volume(3)


while True:
    GO.update()

    if GO.btn_a.was_pressed():
        GO.lcd.print("was_pressed: A")
        GO.speaker.beep()

    if GO.btn_b.was_pressed():
        GO.lcd.print("was_pressed: B")
        GO.speaker.tone(3000, 2)
