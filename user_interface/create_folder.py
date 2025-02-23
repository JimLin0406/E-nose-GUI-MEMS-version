#!venv/bin/python3
# -*- coding: utf-8 -*-
#
# Author: Kevin F. Tung (Yen-Chiang, Tung)
# Organization: National Cheng Kung University, BME, WTMH Lab, 2021, Taiwan
# Copyright © 2021 NCKU WTMH E-Nose Team - All Right Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from PySide2 import QtGui
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QDialog, QFileDialog
from PySide2.QtWidgets import QGridLayout, QFormLayout
from PySide2.QtWidgets import QSizePolicy, QPushButton, QLabel, QLineEdit
from pathlib import Path

class CreateFolderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(760,230)
        self.setup_ui()
        self.set_buttons()
        self.setup_info_container()

    def setup_ui(self):
        self.setWindowTitle('Create New Folder')
        self.setStyleSheet("QWidget{background-color: #1b2042;}")

        widget_creator = WidgetCreator()

        self.create_destination_label = widget_creator.create_label(text='Create destination: ')
        self.create_destination_lineEdit = widget_creator.create_line_edit(placeHolderText='Create folder parent directory')
        self.create_destination_lineEdit.setReadOnly(True)
        self.destinationLayout = QFormLayout()
        self.destinationLayout.addRow(self.create_destination_label, self.create_destination_lineEdit)

        self.create_folder_label = widget_creator.create_label(text='Create folder name: ')
        self.create_folderName_lineEdit = widget_creator.create_line_edit(placeHolderText='New folder name')
        self.folderNameLaout = QFormLayout()
        self.folderNameLaout.addRow(self.create_folder_label, self.create_folderName_lineEdit)

        self.set_destination_btn = widget_creator.createButton('Set path')
        self.create_btn = widget_creator.createButton('Create')
        self.create_btn.setEnabled(False)
        self.cancel_btn = widget_creator.createButton('Cancel')

        g_layout = QGridLayout()
        g_layout.addItem(self.destinationLayout, 0, 0, 1, 2)
        g_layout.addWidget(self.set_destination_btn, 0, 2, 1, 1)
        g_layout.addItem(self.folderNameLaout, 1, 0, 1, 2)
        g_layout.addWidget(self.create_btn, 2, 1, 1, 1)
        g_layout.addWidget(self.cancel_btn, 2, 2, 1, 1)

        self.setLayout(g_layout)

    def set_buttons(self):
        """Setup buttons"""
        self.set_destination_btn.clicked.connect(self.set_destination)
        self.create_btn.clicked.connect(self.create_folder)
        self.create_folderName_lineEdit.textChanged.connect(self.check_create_btn_enable_condition)
        self.cancel_btn.clicked.connect(self.exit)

    def setup_info_container(self):
        self.opened = False
        self.destination = None
        self.create_folder_name = None
        self.create_directory = None

    def has_create_directory(self):
        try:
            dir = Path(self.create_directory)
            return True if dir.is_absolute() else False
        except:
            return False

    @Slot()
    def set_destination(self):
        self.destination = QFileDialog.getExistingDirectory(self, "Select create destination")
        if self.destination:
            self.create_destination_lineEdit.setText(self.destination)
            self.check_create_btn_enable_condition()

    @Slot()
    def check_create_btn_enable_condition(self):
        condition = bool(self.destination) and bool(self.create_folderName_lineEdit.text())
        self.create_btn.setEnabled(condition)

    @Slot()
    def create_folder(self):
        self.create_folder_name = self.create_folderName_lineEdit.text()
        try:
            dir = Path(self.destination, self.create_folder_name)
            self.create_directory = dir if dir.is_absolute() else None
        except:
            self.create_directory = None
        self.close()

    @Slot()
    def exit(self):
        self.create_directory = None
        self.close()
    
class WidgetCreator:

    def default_font(self):
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setWeight(75)
        font.setItalic(False)
        font.setBold(True)
        return font

    def createButton(self, btn_name='Button'):
        button = QPushButton(btn_name)
        button.setFixedSize(130, 40)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy)

        font = self.default_font()
        button.setFont(font)
        button.setStyleSheet('QPushButton{color: rgb(0, 0, 0);\n'
                                         'border-width: 1px;\n'
                                         'border-radius: 10px;\n'
                                         'padding: 5px;\n'
                                         'background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n'
                                                                     'radius: 1.35, stop: 0 #fff, stop: 1 #888);}\n'
                             'QPushButton:pressed {background-color: rgb(5, 112, 112);}\n'
                             'QPushButton:hover:!pressed{background-color: rgb(85, 121, 124);}\n'
                             'QPushButton:disabled{color: rgb(105, 105, 105); background-color: rgb(204, 204, 204);}')
        return button

    def create_label(self, text='LabelText'):
        label = QLabel(text)
        font = self.default_font()
        label.setFont(font)
        label.setStyleSheet('color: rgb(9, 177, 177);')
        return label


    def create_line_edit(self, placeHolderText=''):
        line_edit = QLineEdit()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(line_edit.sizePolicy().hasHeightForWidth())
        line_edit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily('Segoe UI')
        font.setPointSize(12)
        line_edit.setFont(font)
        line_edit.setStyleSheet('QLineEdit{border: 2px solid rgb(9, 177, 177);\n'
                                'border-radius: 10px; \n'
                                'color: rgb(255, 255, 255);\n'
                                'padding: 5px;}')
        line_edit.setText("")
        line_edit.setCursorPosition(0)
        line_edit.setClearButtonEnabled(False)
        line_edit.setPlaceholderText(placeHolderText)
        return line_edit