
from PySide2.QtCore import Qt, Slot, QThread, Signal
from serial.tools import list_ports
from myModules.myqt import QMessageProcessor
from user_interface.window_base import WindowBase
from myModules.taiyo.sensor_control import MonitoringData


class SettingWidget(WindowBase):
    params_signal = Signal(dict)
    dongle_signal = Signal(str)

    def __init__(self,ui_form_path=None):
        super().__init__(ui_form_path)
        self.set_event_connection()
        self._setting_parameter = None
        self.Dongle = None


        self.messenger = QMessageProcessor(self._widget)

    def set_event_connection(self):
        self._widget.save_settings.clicked.connect(self.click_save_settings)
        self._widget.setup_dongle.clicked.connect(self.click_setup_dongle)
        self._widget.refresh_comport.clicked.connect(self.click_refresh_comport)

    @property
    def setting_parameter(self):
        return self._setting_parameter

    @Slot()
    def click_save_settings(self):
        try:
            self.save_parameter()
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeSuccess: 'Set Parameters Successfully!'})
        except ValueError as e:
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeWarning: str(e)})
        except Exception as e:
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeError: f"Error: {str(e)}"})


    def save_parameter(self):
        try:
            keys = ['preparing_time_value', 'measuring_time_value', 'cleaning_time_value'] # UI labels
            param_names = ['Prep_time', 'Measure_time', 'Clean_time']

            values = [int(getattr(self._widget,key).text()) for key in keys]

            if not all(value != 0 for value in values):
                raise ValueError("All input values are zero.")

            self._setting_parameter = dict(zip(param_names, values))
            self.params_signal.emit(self._setting_parameter)


        except ValueError:
            raise ValueError("Invalid input: Please enter a non-zero integer.")


    @Slot()
    def click_setup_dongle(self):
        self.selected_comport = self._widget.comport_combobox.currentText()
        # 是否有選定的COM
        if not self.selected_comport:
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeWarning: 'Please choose comport!'})
        # 是否COM開啟
        self.Dongle = MonitoringData(self.selected_comport)
        if self.Dongle.check_connect():
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeSuccess: 'Successfully connect comport!'})
            self.Dongle.close()
            self.dongle_signal.emit(self.selected_comport)
        else:
            self.messenger.messageBroadcast(
                {QMessageProcessor.TypeWarning: 'Fail to connect comport!'})

    @Slot()
    def click_refresh_comport(self):
        if self.Dongle is not None:
            self.Dongle.close()
        self._widget.comport_combobox.clear()
        comports = list_ports.comports()

        for comport in comports:
            self._widget.comport_combobox.addItem(comport.device, Qt.AlignRight)


