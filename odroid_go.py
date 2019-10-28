from machine import Pin, SPI, ADC
from utils import *


class ODROID_GO:
    """
    Class for helping to code with ODROID-GO.
    """

    def __init__(self):
        self._init_lcd()
        self._init_buttons()
        self._init_speaker()
        self._init_battery()

    def _init_lcd(self):
        self.lcd = ILI9341(SPI(2, baudrate=40000000,
                               miso=Pin(TFT_MISO_PIN, Pin.IN),
                               mosi=Pin(TFT_MOSI_PIN, Pin.OUT),
                               sck=Pin(TFT_SCLK_PIN, Pin.OUT)),
                           cs=Pin(TFT_CS_PIN, Pin.OUT),
                           dc=Pin(TFT_DC_PIN, Pin.OUT))

    def _init_buttons(self):
        self.btn_joy_x = Button(BUTTON_JOY_X_PIN, True, BUTTON_DEBOUNCE_MS)
        self.btn_joy_y = Button(BUTTON_JOY_Y_PIN, True, BUTTON_DEBOUNCE_MS)
        self.btn_menu = Button(BUTTON_MENU_PIN, True, BUTTON_DEBOUNCE_MS)
        self.btn_volume = Button(BUTTON_VOLUME_PIN, True, BUTTON_DEBOUNCE_MS)
        self.btn_select = Button(BUTTON_SELECT_PIN, True, BUTTON_DEBOUNCE_MS)
        self.btn_start = Button(BUTTON_START_PIN, True, BUTTON_DEBOUNCE_MS)
        self.btn_a = Button(BUTTON_A_PIN, True, BUTTON_DEBOUNCE_MS)
        self.btn_b = Button(BUTTON_B_PIN, True, BUTTON_DEBOUNCE_MS)

    def _init_speaker(self):
        self.speaker = Speaker(SPEAKER_PIN, SPEAKER_DAC_PIN)

    def _init_battery(self):
        self.battery = Battery(BATTERY_PIN, BATTERY_RESISTANCE_NUM,
                               ADC.WIDTH_12BIT, ADC.ATTN_11DB)

    def begin(self):
        # LCD
        self.lcd.erase()
        self.lcd.fill(colors.BLACK)
        self.lcd.set_pos(0, 0)
        self.lcd.colors = colors
        self.lcd.fonts = fonts
        Pin(TFT_LED_PIN, Pin.OUT).value(1)

        # Buttons
        Pin(BUTTON_JOY_X_PIN, Pin.IN)
        Pin(BUTTON_JOY_Y_PIN, Pin.IN)
        Pin(BUTTON_MENU_PIN, Pin.IN, Pin.PULL_UP)
        Pin(BUTTON_VOLUME_PIN, Pin.IN, Pin.PULL_UP)
        Pin(BUTTON_SELECT_PIN, Pin.IN, Pin.PULL_UP)
        Pin(BUTTON_START_PIN, Pin.IN)
        Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)
        Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)

        # Speaker
        self.speaker.set_volume(0.1)
        self.speaker.set_beep(262, 1)

    def update(self):
        self.btn_joy_x.read_axis()
        self.btn_joy_y.read_axis()
        self.btn_menu.read()
        self.btn_volume.read()
        self.btn_select.read()
        self.btn_start.read()
        self.btn_a.read()
        self.btn_b.read()


GO = ODROID_GO()
GO.begin()
GO.lcd.fill(colors.BLUE)
GO.lcd.fill_rectangle(0,0, 100,100, colors.WHITE )
