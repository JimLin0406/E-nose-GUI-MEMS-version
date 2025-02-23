#!venv/bin/python3

# Author: Kevin Tung (Yen-Chiang, Tung) <kevin.wtmh@gmail.com>
# Organization: National Cheng Kung University, BME, WTMH Lab, 2022, Taiwan
# License: BSD 3 clause

import Jetson.GPIO as GPIO
from sys import platform
GPIO.setwarnings(False)

class PlatformError(Exception):
    "PlatformError"

def cleanup(pin=None):
    if pin:
        GPIO.cleanup(pin)
    else:
        GPIO.cleanup()

class BaseGPIOControl:
    def __init__(self, pin) -> None:
        self._check_platform()

        if pin is None:
            raise Exception("pin can not be None")

        self.pin = pin
        self.state = None

        # Pin Setup:
        GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)  # control pin set as output
 
    def _check_platform(self):
        if platform!="linux":
            raise PlatformError("Only Linux OS is acceptable")
        
        valid_jetson_platform = [
            'JETSON_XAVIER',
            'CLARA_AGX_XAVIER',
            'JETSON_TX2',
            'JETSON_TX2_NX',
            'JETSON_NANO'
            # others: JETSON_NANO, JETSON_NX, JETSON_ORIN
        ]
        if GPIO.model not in valid_jetson_platform:
            raise PlatformError(f"Pump control is not "
                                f"support on {GPIO.model} platform")
  
    def _output(self, state):
        if self.state!=state:
            GPIO.output(self.pin, state)
            self.state = state

    def enable(self):
        self._output(GPIO.HIGH)
  
    def disable(self):
        self._output(GPIO.LOW)

    def cleanup(self):
        cleanup(self.pin)
     
class ExtraPumpA(BaseGPIOControl):
    def __init__(self) -> None:
        output_pins = {
            'JETSON_XAVIER': 12,
            'CLARA_AGX_XAVIER': 12,
            'JETSON_TX2': 12,
            'JETSON_TX2_NX': 12,
            'JETSON_NANO': 12
        }
        super().__init__(output_pins.get(GPIO.model, None))

class ExtraPumpB(BaseGPIOControl):
    def __init__(self) -> None:
        output_pins = {
            'JETSON_XAVIER': 13,
            'CLARA_AGX_XAVIER': 13,
            'JETSON_TX2': 13,
            'JETSON_TX2_NX': 13,
            'JETSON_NANO': 13
        }
        super().__init__(output_pins.get(GPIO.model, None))

class ExtraValve(BaseGPIOControl):
    def __init__(self) -> None:
        output_pins = {
            'JETSON_XAVIER': 15,
            'CLARA_AGX_XAVIER': 15,
            'JETSON_TX2': 15,
            'JETSON_TX2_NX': 15,
            'JETSON_NANO': 15
        }
        super().__init__(output_pins.get(GPIO.model, None))