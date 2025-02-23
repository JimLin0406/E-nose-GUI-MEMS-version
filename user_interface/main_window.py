
from collections import OrderedDict

from PySide2.QtCore import Qt, QEvent, QFile, QSize, Slot
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow,QStatusBar,QListWidget, QListView, QListWidgetItem

from user_interface.measure_page import MeasureWidget
from user_interface.setting_page import SettingWidget

__copyright__ = 'Copyright © 2025 NCKU WTMH E-Nose Team - All Right Reserved.'
__windowTitle__ = 'WTMH - Smell Sensor UI Framework (MEMS version)'

stylesheet = """
    QWidget {
        background-image: url(./user_interface/media/backgound-1.png);
        background-repeat: no-repeat;
    }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self._window = None
        self._option_panel = None
        self._pages = OrderedDict()
        self.ui_setup()


    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self._window.close()
        return super(MainWindow, self).eventFilter(obj, event)

    @property
    def window(self):
        """MainWindow widget."""
        return self._window

    def ui_setup(self):
        """Initialize user interface of main window."""
        loader = QUiLoader()
        file = QFile('./user_interface/form/main_window.ui')
        file.open(QFile.ReadOnly)
        self._window = loader.load(file)
        self._window.installEventFilter(self)  # install Event Filter to let user can implement key press event
        file.close()

        status_bar = QStatusBar(self._window)
        status_bar.showMessage(__copyright__)
        status_bar.setStyleSheet("QStatusBar{background-color: rgb(30, 43, 51); color: rgb(0, 175, 151);}")
        self._window.setStatusBar(status_bar)
        self._window.setStyleSheet("background-color: rgb(30, 43, 51); color: rgb(9, 177, 177)")

        self._window.setWindowIcon(QIcon('./user_interface/media/ENose_logo_02.png'))
        self._window.setWindowTitle(__windowTitle__)

        self._option_panel = OptionPanel()
        self._option_panel.add_button('Measure', './user_interface/media/measure-1.png')
        self._option_panel.add_button('Setting', './user_interface/media/setting-1.png')

        # Add widget to main layout
        main_layout = self._window.gridLayout
        main_layout.itemAtPosition(0, 0).setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self._option_panel, 1, 0, 1, 1)

        # Add page widget to stack
        self._pages['measure'] = MeasureWidget('./user_interface/form/measure_widget.ui')
        self._pages['setting'] = SettingWidget('./user_interface/form/setting_widget.ui')

        for index, name in enumerate(self._pages):
            print('pages {} : {} page'.format(index, name))
            self._window.widget_stack.addWidget(self._pages[name].widget)

        self._window.widget_stack.setCurrentIndex(0)

        # Build up signal / slot
        self._option_panel.currentItemChanged.connect(self.set_page)

        # Send data from pages to pages
        self._pages['setting'].params_signal.connect(self._pages['measure']._setting_pram)
        self._pages['setting'].dongle_signal.connect(self._pages['measure']._dongle)




    @Slot(int, int)
    def set_page(self, current, previous):
        """Slot, switch shown page."""
        widget_num = self._option_panel.currentIndex().row()
        self._option_panel.item(widget_num).setSelected(True)
        self._window.widget_stack.setCurrentIndex(widget_num)

class OptionPanel(QListWidget):
    STYLE = 'QListWidget { border : none solid  #404244;' \
            'font : 10pt bold \"Source Code Pro\";' \
            'background-color: #35388B; color: #d3d7cf; outline: none;}' \
            'QListWidget::Item {border-bottom: 1px solid #999999;}' \
            'QListWidget::item:hover { background-color: ' \
            'qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,' \
            ' stop: 1 #4d4d4d, stop: 0 transparent); color: #10a2a5;}' \
            'QListView::item:selected { background-color:' \
            'qlineargradient( x1: 0, y1: 0, x2: 0, y2: 1,' \
            ' stop: 1 transparent, stop: 0 #ffffff); color: #03f3f4;}'

    def __init__(self,parent=None):
        super(OptionPanel,self).__init__(parent)
        self._options_buttons = OrderedDict()

        self.setCurrentRow(0)
        self.setMaximumWidth(65)
        self.setMinimumSize(QSize(65, 400))
        self.setViewMode(QListView.IconMode)
        self.setMovement(QListView.Static)
        self.setIconSize(QSize(40, 40))
        self.setSpacing(3)
        self.setItemAlignment(Qt.AlignCenter)
        self.setEnabled(True)
        self.setStyleSheet(self.STYLE)

    def add_button(self, name, icon):
        self._options_buttons[name] = self.create_item(name,icon)
        self.addItem(self._options_buttons[name])

    def create_item(self, name, icon):
        """Create a standard list widget item, for option panel.

        Args:
          name: Name of option button
          icon: Icon name of option button
        Returns:
          item: created option button
        """
        item = QListWidgetItem(self)
        item.setText(name)
        item.setIcon(QIcon(icon))
        item.setStatusTip(name)
        item.setSizeHint(QSize(60, 70))
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        return item
