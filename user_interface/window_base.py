
"""Window base
"""

from PySide2.QtCore import QObject, QFile, QSettings
from PySide2.QtUiTools import QUiLoader

from typing import Optional


app_settings: Optional[QSettings] = None


class WindowBase(QObject):
    def __init__(self, ui_form_path=None):
        super().__init__()
        self._setup_ui(ui_form_path)

    @property
    def widget(self):
        return self._widget

    def _setup_ui(self, ui_form_path=None):
        try:
            loader = QUiLoader()
            file = QFile(ui_form_path)
            file.open(QFile.ReadOnly)
            self._widget = loader.load(file)
            file.close()

        except Exception as e:
            print(e)
            raise
