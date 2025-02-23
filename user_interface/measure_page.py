import time
from sys import platform
import numpy as np
import os
import csv
from datetime import datetime
from copy import deepcopy
from PySide2.QtCore import Qt, Slot, QThread, Signal, QTimer
from PySide2.QtWidgets import QFileDialog
from PySide2.QtGui import QColor
from myModules.myqt import QRoundProgressBar, QMessageProcessor, QPolarChart
from user_interface.create_folder import CreateFolderDialog
from user_interface.window_base import WindowBase
from myModules.taiyo.sensor_control import MonitoringData
from datetime import date
from pathlib import Path
from itertools import cycle

SC_RET_LEN = 20
CHANNEL_NUM = 8

SENSOR_STATE = {
    0: "IDLE",
    1: "PREPARE",
    2: "MEASURE",
    3: "CLEAN",
    4: "DISCONNECT"
}
IDLE = SENSOR_STATE[0]
PREP = SENSOR_STATE[1]
MEASURE = SENSOR_STATE[2]
CLEAN = SENSOR_STATE[3]
DISCONNECT = SENSOR_STATE[4]


class MeasureWidget(WindowBase):

    def __init__(self,ui_form_path=None):
        super().__init__(ui_form_path)

        self.setting_parameter = None
        # self.Dongle = None
        self.state = DISCONNECT

        self.set_event_connection()
        self.setup_monitors()
        self.setup_monitering_threads()
        self.setup_save_destination()
        self.messenger = QMessageProcessor(self._widget)
        self.create_folder_dialog = CreateFolderDialog(self._widget)

    @Slot()
    def _dongle(self, ser):
        # self.Dongle = don
        self.ser = ser
        self.state = IDLE
        global current_data
        current_data = ["IDLE"]

    @Slot()
    def _setting_pram(self,dict):
        global setting_parameter
        setting_parameter = dict
        self.setting_parameter = dict

    def set_event_connection(self):
        self._widget.start_measure_btn.clicked.connect(self.start_measurement)
        self._widget.create_folder_btn.clicked.connect(self.create_new_folder)
        self._widget.set_destination_btn.clicked.connect(self.set_save_destination)

    def setup_monitors(self):
        self.sensorState_monitor = SensorStateMonitor(self._widget.realtime_view_sensor_text,
                                                      self._widget.current_mode_text)
        self.progress_monitor = ProgressMonitor(self._widget.measuring_progress,
                                                self._widget.remain_time)
        self.deltaData_monitor = MeasureRadarMonitor()
        self.temperature_monitor = TemperatureMonitor()
        self.humidity_monitor = HumidityMonitor()
        self.pressure_monitor = PressureMonitor()
        self.extra_component_monitor = ExtraComponentMonitor()

        # add monitors to a grid layout (widget, row, column, rowSpan, columnSpan)
        self._widget.statusBar_gridLayout.addWidget(self.deltaData_monitor.chartView, 0, 0, 3, 1)
        self._widget.statusBar_gridLayout.addWidget(self.temperature_monitor, 0, 1, 1, 1)
        self._widget.statusBar_gridLayout.addWidget(self.humidity_monitor, 1, 1, 1, 1)
        self._widget.statusBar_gridLayout.addWidget(self.pressure_monitor, 2, 1, 1, 1)
        self._widget.statusBar_gridLayout.setContentsMargins(0, 0, 0, 0)

        # attach the monitors to monitor manager
        self.monitors_manager = MonitorsManager()
        self.monitors_manager.attach(self.sensorState_monitor)
        self.monitors_manager.attach(self.progress_monitor)
        self.monitors_manager.attach(self.deltaData_monitor)
        self.monitors_manager.attach(self.temperature_monitor)
        self.monitors_manager.attach(self.humidity_monitor)
        self.monitors_manager.attach(self.pressure_monitor)
        self.monitors_manager.attach(self.extra_component_monitor)

    def setup_monitering_threads(self):
        self.monitors_updater = MonitorsUpdater()
        self.monitors_updater.update_monitor_signal.connect(self.monitors_manager.update_data)
        self.monitors_updater.start()


    def setup_save_destination(self):
        home_path = str(Path.home())
        if "AppData" in home_path:
            home_path = home_path.partition("\\AppData")[0]
        today_date = date.today().strftime('%Y-%m-%d')
        self.save_destination = Path(home_path, "Downloads", f'{today_date}-measured')

    @Slot()
    def start_measurement(self):
        if self._widget.sample_name.text() != '':
            self.measurement_name = self._widget.sample_name.text()
            if not Path(self.save_destination, f'{self.measurement_name}.csv').exists():
                pass
            else:
                self.messenger.messageBroadcast(
                    {QMessageProcessor.TypeWarning: 'File name of sample already '
                                                    'exists in the destination folder!'})
                return
            if self.setting_parameter is not None:
                if self.state == IDLE:
                    # self.Dongle.run()
                    self.csv_data = []
                    self.state = PREP
                    self.start_measure_thread()
                elif self.state == PREP or self.state == MEASURE or self.state == CLEAN:
                    self.messenger.messageBroadcast(
                        {QMessageProcessor.TypeWarning: 'Already measuring!'})
                    return
                else:
                    self.messenger.messageBroadcast(
                        {QMessageProcessor.TypeError: 'Measurement failed!'})
                    return
            else:
                self.messenger.messageBroadcast(
                    {QMessageProcessor.TypeWarning: 'Must set up parameters and connect to comport before start measure!'})
                return
        else:
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeError: 'Must input the sample name before start measure!'})
            return

    def start_measure_thread(self) -> None:

        self.__thread = QThread()
        self.__worker = MonitoringData(self.ser)
        self.__worker.moveToThread(self.__thread)
        self.__worker.open_and_run()
        self.__worker.received_data.connect(self.process_received_data)
        self.__thread.started.connect(self.__worker.read_data)
        self.__thread.finished.connect(self.__thread_finished)
        self.__thread.start()
        print("Start data collection...")

    @Slot(str)
    def process_received_data(self, data) -> None:
        # 檢查數據數量是否正常
        if len(data.split(',')) == SC_RET_LEN:
            self.process(data)

    def process(self,line:str) -> None:
        if self.state == PREP:
            if len(self.csv_data) == int(self.setting_parameter["Prep_time"]):
                print(f"{self.state} phase finished...")
                self.state = MEASURE
            print(self.state + ':' + line)
        elif self.state == MEASURE:
            if len(self.csv_data) == (int(self.setting_parameter["Prep_time"])+int(self.setting_parameter["Measure_time"])):
                print(f"{self.state} phase finished...")
                self.state = CLEAN
            print(self.state + ':' + line)
        elif self.state == CLEAN:
            if len(self.csv_data) == (int(self.setting_parameter["Prep_time"])+int(self.setting_parameter["Measure_time"])+int(self.setting_parameter["Clean_time"])):
                print(f"{self.state} phase finished...")
                self.state = IDLE

                self.create_csv_and_save()

                self.finish_measurement()

            print(self.state + ':' + line)

        self.raw_data = line.split(',')
        now = datetime.today()
        time = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
        phase_buf = self.state
        # 將資訊儲存在變數中以用於 CSV 輸出
        self.csv_data.append(
            [time]
            + [len(self.csv_data) + 1]
            + [phase_buf]
            + self.raw_data[:9]
            + self.raw_data[-3:]
        )

        global current_data
        current_data = deepcopy([phase_buf] + self.raw_data[:9]+self.raw_data[-3:])

    def create_csv_and_save(self) -> str:
        csv_data = deepcopy(self.csv_data)
        # CSV title
        data_label = (
                ['time', 'No', 'step', 'Num']
                + [('ch' + str(i + 1)) for i in range(CHANNEL_NUM)]
                + ['Humi', 'Temp', 'pressure',]
        )
        # CSV title
        csv_data.insert(0, data_label)

        file_name = os.path.join(self.save_destination, f'{self.measurement_name}.csv')
        path = self.save_destination
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(file_name, 'w', newline='', encoding='shift_jis') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)

    def finish_measurement(self):
        self.__worker.stop()
        self.__thread.quit()
        self.__thread.wait()


    @Slot()
    def __thread_finished(self) -> None:
        self.__thread.deleteLater()
        # Delete the __worker to not emit any signal
        del self.__worker

    @Slot()
    def create_new_folder(self):
        if not self.create_folder_dialog.opened:
            self.create_folder_dialog.opened = True
            self.create_folder_dialog.show()
            self.create_folder_dialog.exec_()

            try:
                if self.create_folder_dialog.has_create_directory():
                    dir = self.create_folder_dialog.create_directory
                    if not Path.exists(dir):
                        Path.mkdir(dir)
                        self.save_destination = dir
                        self.messenger.messageBroadcast(
                            {QMessageProcessor.TypeSuccess: 'Success create new folder!'})
                    else:
                        self.messenger.messageBroadcast(
                            {QMessageProcessor.TypeWarning: 'Folder already exists!'})
            except:
                self.messenger.messageBroadcast(
                    {QMessageProcessor.TypeError: 'Can not create new folder.'})
            self.create_folder_dialog.opened = False

    @Slot()
    def set_save_destination(self):
        directory = Path(QFileDialog.getExistingDirectory(
            self._widget, "Select Top Level Directory"))
        if directory.is_absolute():
            self.save_destination = directory
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeSuccess: f'The download destination changed '
                                                f'to {self.save_destination}!'})


###################################
#
#   Monitoring Chart :
#       SensorSate
#       RadarPlot
#       Humidity, Temperature, Pressure
#       ProgressBar
#
class MonitorsManager:
    def __init__(self) -> None:
        self.monitors = []
        self.realtime_data = []

    def attach(self, monitor=None):
        self.monitors.append(monitor)

    def detach(self, monitor=None):
        self.monitors.remove(monitor)

    def update_data(self, data):
        self.realtime_data = data
        self.__notify()

    def __notify(self):
        for monitor in self.monitors:
            try:
                monitor.refresh(self.realtime_data)
            except:
                print(f'Monitor {monitor.__class__.__name__} can not refresh.')
class SensorStateMonitor:
    def __init__(self, sensor_mac_label=None, sensor_state_label=None) -> None:
        self.sensor_mac_label = sensor_mac_label
        self.sensor_state_label = sensor_state_label
        self.text_effect = True

        self.text_color = {
            IDLE: cycle(["#00E88F"]),
            PREP: cycle(["#00A0E9"]),
            MEASURE: cycle(["#E80000", '#f0f0f0']),
            CLEAN: cycle(["#00A0E9"]),
            DISCONNECT: cycle(["red"]),
        }
        self.sensor_mac_label.setText("MEMS Enose")

    def refresh(self, realtime_data: dict):
        state = realtime_data.get('state', None)
        # state = state if state in self.text_transform.keys() else None
        # self.sensor_mac_label.setText("any")
        self.sensor_state_label.setText(state)
        self.sensor_state_label.setStyleSheet(f"color: {next(self.text_color[state])}")

class MeasureRadarMonitor(QPolarChart):
    def __init__(self, channels: int = 8, reverse: bool = True):
        super().__init__(channels=channels, reverse=reverse)
        self.visible_option = {
            IDLE: False,
            PREP: False,
            MEASURE: True,
            CLEAN: True,
        }

        self.update(np.zeros(8, dtype=int))

    def refresh(self, realtime_data: dict):
        visible = self.visible_option.get(realtime_data['state'], False)
        data = realtime_data.get('channels_delta', None)
        data = data if visible else None
        self.update(data)
        self.setVisible(visible)

class TemperatureMonitor(QRoundProgressBar):
    def __init__(self):
        super().__init__()
        self.title = "Temp."
        unit = u"\N{DEGREE SIGN}C"
        self.setFormat(f'{self.title}\n%s {unit}')
        self.setDataColors([(0., QColor('#4075b3')), (1., QColor('48afcf'))])
        self.setRange(0, 90)

    def refresh(self, realtime_data: dict):
        self.setValue(round(float(realtime_data.get('temperature', 0)), 1))

class HumidityMonitor(QRoundProgressBar):
    def __init__(self):
        super().__init__()
        self.title = "Humidity"
        self.setFormat(f'{self.title}\n%s %')
        self.setDataColors([(0., QColor('#52b2c3')), (1., QColor('#67b894'))])
        self.setRange(0, 100)

    def refresh(self, realtime_data: dict):
        self.setValue(round(float(realtime_data.get('humidity', 0)), 1))

class PressureMonitor(QRoundProgressBar):
    def __init__(self):
        super().__init__()
        self.title = "Pressure"
        self.setFormat(f'{self.title}\n%s hPa')
        self.setDataColors([(0., QColor('#4075b3')), (1., QColor('#67b894'))])
        self.setRange(0, 1500)

    def refresh(self, realtime_data: dict):
        self.setValue(round(float(realtime_data.get('pressure', 0)), 1))

class ProgressMonitor:
    def __init__(self, progressBar_widget=None, remainTime_widget=None):
        self.progressBar_widget = progressBar_widget
        self.remainTime_widget = remainTime_widget

    def refresh(self, realtime_data):
        remaining_time = realtime_data['progress'][0]
        progress = realtime_data['progress'][1]
        self.remainTime_widget.setText(str(remaining_time))
        self.progressBar_widget.setValue(round(progress, 1))


class ExtraComponentMonitor:
    def __init__(self):
        # Control pumps and valve by NVIDIA Jetson
        if platform == 'linux':
            from myModules.control import ExtraPumpA, ExtraPumpB, ExtraValve
            self.pump_A = ExtraPumpA()
            self.pump_B = ExtraPumpB()
            self.valve = ExtraValve()

    @property
    def has_pumps(self):
        pumps = ["pump_A", "pump_B"]
        return True if all(hasattr(self, attr) for attr in pumps) else False

    def refresh(self, realtime_data):
        if self.has_pumps:
            state = realtime_data['state']
            if state in [PREP, CLEAN]:
                self.pump_A.enable()
                self.pump_B.disable()
                self.valve.disable()
            elif state == MEASURE:
                self.pump_A.disable()
                self.pump_B.enable()
                self.valve.enable()
            else:
                self.pump_A.disable()
                self.pump_B.disable()
                self.valve.disable()

class MonitorsUpdater(QThread):
    update_monitor_signal = Signal(object)
    def __init__(self):
        super().__init__()
        self.refresh_time = 500  # milli-second
        self._reset_realtime_status()

    def _reset_realtime_status(self):
        self.last_state = DISCONNECT
        self.current_state = DISCONNECT
        self.progress_counter = 0
        self.sensor_realtime = {'state': self.current_state,
                                'channels_delta': np.zeros(16),
                                'temperature': 0,
                                'humidity': 0,
                                'pressure': 0,
                                'progress': [None, 0]}

    def _get_measuring_progress(self):
        try:
            global setting_parameter
            self.setting = setting_parameter
            progress_time = {
                PREP: int(self.setting['Prep_time'])*1000,  # in second
                MEASURE: int(self.setting['Measure_time'])*1000,
                CLEAN: int(self.setting['Clean_time'])*1000,
            }
            if self.state in [PREP, MEASURE, CLEAN]:
                self.current_state = self.state
                progress_time = progress_time[self.current_state]

                if self.current_state != self.last_state:
                    # reset progress counter
                    self.progress_counter = self.refresh_time
                else:
                    if self.progress_counter < progress_time:
                        self.progress_counter += self.refresh_time

                remaining_time = f'{self.progress_counter/1000}s / {progress_time/1000}s'
                progress = (self.progress_counter / progress_time) * 100
                self.last_state = self.current_state
            else:
                self.progress_counter = 0
                remaining_time = None
                progress = 0
            return [remaining_time, progress]
        except Exception as e:
            print(e)
            raise

    def _get_sensor_current_data(self) -> dict:
        try:
            global current_data
            realtime_info = dict()
            channel_data = list(map(int, current_data[2:10]))
            if len(channel_data) == 8:
                realtime_info['channels_delta'] = np.array(channel_data)
            else:
                realtime_info['channels_delta'] = np.zeros(8, dtype=int)

            self.state = str(current_data[0])

            realtime_info['state'] = self.state
            realtime_info['humidity'] = float(current_data[10])
            realtime_info['temperature'] = float(current_data[11])
            realtime_info['pressure'] = float(current_data[12])
            realtime_info['progress'] = self._get_measuring_progress()
            return realtime_info
        # Initially, it shows " 'current_data' is not defined ".
        except:
            return realtime_info

    def run(self):
        def _work():
            realtime_data: dict = self._get_sensor_current_data()
            if realtime_data is not None:
                self.sensor_realtime.update(realtime_data)
            self.update_monitor_signal.emit(self.sensor_realtime)

        timer = QTimer()
        timer.timeout.connect(_work)
        timer.start(self.refresh_time)
        self.exec_()