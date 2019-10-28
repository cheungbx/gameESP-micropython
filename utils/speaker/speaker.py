"""
A simple speaker module for Micropython (ESP32).

Created on: 2018. 7. 10
Author: Joshua Yang (joshua.yang@hardkernel.com)
"""

from machine import PWM, Pin
import utime


class Speaker:
    _speaker_pin = object()
    _speaker_pwm = object()
    _dac_pin = object()
    _beep_duration = 0
    _beep_frequency = 0
    _volume_duty = 0

    def __init__(self, pin, dac_pin, frequency=262, duration=0, volume=1):
        self._speaker_pin = Pin(pin, Pin.OUT, value=1)
        self._speaker_pwm = PWM(self._speaker_pin, duty=0)
        self._dac_pin = Pin(dac_pin, Pin.OUT, value=1)

        self.set_beep(frequency, duration)
        self.set_volume(volume)

    def _dac_switch(self, switch=None):
        if switch is None:
            self._dac_pin.value(1 if self._dac_pin.value() == 0 else 0)
        else:
            self._dac_pin.value(switch)

    # TODO: It should run as in non-blocking way (async, thread, ...)
    def _play_tone(self, frequency=None, duration=None):
        self._speaker_pwm.freq(self._beep_frequency if frequency is None else frequency)
        self._speaker_pwm.duty(self._volume_duty)

        utime.sleep(self._beep_duration if duration is None else duration)
        self._speaker_pwm.duty(0)

    def tone(self, frequency=None, duration=None):
        self._play_tone(frequency, duration)

    def beep(self):
        self.tone()

    def mute(self):
        self._dac_switch(0)

    def toggle_mute(self, switch=None):
        self._dac_switch(switch)

    def set_volume(self, volume=None):
        if volume is None:
            print(str(self._volume_duty) + "/" + str(self._volume_duty / 1023 * 100) + " %")
        elif not 0 <= volume <= 10:
            print("Volume value must be from 0 to 10")
        else:
            self._dac_switch(1)
            self._volume_duty = round(volume * 10 * 10.23)

    def set_beep(self, frequency=None, duration=None):
        if frequency is None and duration is None:
            print(str(self._beep_frequency) + "/" + str(self._beep_duration))
        else:
            self._beep_frequency = self._beep_frequency if frequency is None else frequency
            self._beep_duration = self._beep_duration if duration is None else duration

    # TODO: Not implemented yet
    def play_music(self, music_data, sample_rate):
        pass
