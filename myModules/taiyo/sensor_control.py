import serial
import time

from PySide2.QtCore import Signal,QObject
from PySide2.QtCore import Qt, Slot, QThread, Signal, QTimer



class MonitoringData(QObject):
    """A class for monitoring and handling serial communication.

    Attributes:
        received_data (Signal): A signal that emits received serial data as a string.
        port (str): The serial port to connect to.
        baudrate (int): The baud rate for the serial communication (default: 115200).
        timeout (int): Serial timeout in milliseconds (default: 500).
        running (bool): A flag indicating whether data reading is active.
        serial (serial.Serial): The serial port connection object.
    """

    # Signal emitted when new serial data is received
    received_data = Signal(str)

    def __init__(self, port = None):
        """
        Args:
            port (str, optional): The serial port to connect to. Defaults to None.
        """

        super().__init__()
        self.port = port
        self.baudrate = 115200
        self.timeout = 500

        self.running = False
        self.serial = None

    def open(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        except serial.SerialException as e:
            print(e)

    def check_connect(self):
        """
        Checks if the serial device is responding.

        Returns:
            bool: True if the device sends a response, otherwise False.
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)
            if self.serial.in_waiting > 0:
                data = self.serial.read(self.serial.in_waiting).decode('utf-8').strip()
                if any(x in data for x in ["\n", "\r"]):
                    return True
            return False

        except serial.SerialException as e:
            print(e)


    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.serial = None

    def read_data(self):
        while self.running:
            if self.serial and self.serial.is_open:
                try:
                    self.serial.reset_input_buffer()
                    data = self.serial.readline().decode('utf-8').strip()
                    self.received_data.emit(data)

                except serial.SerialException:
                    self.open()
                    self.close()

            time.sleep(0.1)
    def stop(self):
        self.running = False
    def run(self):
        self.running = True
    def open_and_run(self):
        self.open()
        self.run()

@Slot(str)
def process_received_data(data) -> None:
    print(f"Received data:",data)

if __name__ == "__main__":
    worker = MonitoringData("COM16")
    worker.open()
    worker.run()

    worker.received_data.connect(process_received_data)
    worker.read_data()