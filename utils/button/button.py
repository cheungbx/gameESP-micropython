"""
A Micropython port of Arduino Button Library.

Created on: 2018. 7. 6
Author: Joshua Yang (joshua.yang@hardkernel.com)

/*----------------------------------------------------------------------*
 * Arduino Button Library v1.0                                          *
 * Jack Christensen May 2011, published Mar 2012                        *
 *                                                                      *
 * Library for reading momentary contact switches like tactile button   *
 * switches. Intended for use in state machine constructs.              *
 * Use the read() function to read all buttons in the main loop,        *
 * which should execute as fast as possible.                            *
 *                                                                      *
 * This work is licensed under the Creative Commons Attribution-        *
 * ShareAlike 3.0 Unported License. To view a copy of this license,     *
 * visit http://creativecommons.org/licenses/by-sa/3.0/ or send a       *
 * letter to Creative Commons, 171 Second Street, Suite 300,            *
 * San Francisco, California, 94105, USA.                               *
 *----------------------------------------------------------------------*/
"""

from machine import Pin, ADC
import utime


class Button:
    _pin = object()
    _invert = 0
    _state = 0
    _last_state = 0
    _changed = 0
    _axis = 0
    _time = 0
    _last_time = 0
    _last_change = 0
    _db_time = 0

    _debug_mode = False

    def __init__(self, pin, invert, db_time):
        if pin < 34 :
            self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        else :
            self._pin = Pin(pin, Pin.IN)
        self._invert = invert
        self._db_time = db_time

        self._state = self._pin.value()
        if self._invert != 0:
            self._state = not self._state
        self._time = utime.ticks_ms()
        self._last_state = self._state
        self._last_time = self._time
        self._last_change = self._time

        # self._debug_mode = True

    def _debug_message(self, results):
        if self._debug_mode:
            print(results)

    def read(self):
        ms = utime.ticks_ms()
        pin_val = self._pin.value()

        if self._invert != 0:
            pin_val = not pin_val

        if ms - self._last_change < self._db_time:
            self._last_time = self._time
            self._time = ms
            self._changed = 0

            return self._state
        else:
            self._last_time = self._time
            self._last_state = self._state
            self._state = pin_val
            self._time = ms

            if self._state != self._last_state:
                self._last_change = ms
                self._changed = 1
            else:
                self._changed = 0

            return self._state

    def read_axis(self):
        apin = ADC(self._pin)
        apin.atten(ADC.ATTN_11DB)
        val = apin.read()

        ms = utime.ticks_ms()
        pin_val = 0

        self._debug_message("val: " + str(val))

        if val > 3900:
            pin_val = 1
            self._axis = 2
        elif 1500 < val < 2000:
            pin_val = 1
            self._axis = 1
        else:
            pin_val = 0
            self._axis = 0

        if self._invert == 0:
            pin_val = not pin_val

        if ms - self._last_change < self._db_time:
            self._last_time = self._time
            self._time = ms
            self._changed = 0
        else:
            self._last_time = self._time
            self._last_state = self._state
            self._state = pin_val
            self._time = ms

            if self._state != self._last_state:
                self._last_state = ms
                self._changed = 1
            else:
                self._changed = 0

        return self._state

    def is_pressed(self):
        return 0 if self._state == 0 else 1

    def is_axis_pressed(self):
        return self._axis if self._state else 0

    def is_released(self):
        return 1 if self._state == 0 else 0

    def was_pressed(self):
        return self._state and self._changed

    def was_axis_pressed(self):
        return self._axis if self._state and self._changed else 0

    def was_released(self):
        return (not self._state) and self._changed

    def pressed_for(self, ms):
        return 1 if (self._state == 1 and self._time - self._last_change >= ms) else 0

    def released_for(self, ms):
        return 1 if (self._state == 0 and self._time - self._last_change >= ms) else 0

    def last_change(self):
        return self._last_change
