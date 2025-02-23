
import os, sys

from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QApplication
from user_interface.main_window import MainWindow

import faulthandler

faulthandler.enable()

app_source_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_source_directory)
print(f'User interface source code directory: {app_source_directory}')

if  __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = '1'
    # os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.window.setFixedSize(QSize(960, 540))
    # main_window.window.setFixedSize(QSize(1080, 600))
    flags = main_window.window.windowFlags()
    main_window.window.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
    main_window.window.show()
    sys.exit(app.exec_())