#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################
# Message tools for PySide2
#
# Author: Kevin Tung (NCKU.BME.2021)
#
# Organization: Biomedical Engineering, National Cheng Kung University, Taiwan
#
# Edit Year: 2021
#######################################################
from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QMessageBox

class QRunnableSignal(QObject):
    emitter = Signal(object)

class QMessageProcessor:
    TypeSuccess = 'Operation successful'
    TypeWarning = 'Warning'
    TypeError = 'Error'

    def __init__(self, parent=None):
        self.parent = parent
        self.broadcasters = {self.TypeSuccess: QMessageBox.information,
                             self.TypeWarning:  QMessageBox.warning,
                             self.TypeError: QMessageBox.critical}

    def messageBroadcast(self, signal):
        messageType, content = list(*signal.items())
        broadcasters = self.broadcasters.get(messageType, lambda: 'Wrong message type.')
        broadcasters(self.parent, messageType,  f'<font size=5 color=white> {content} </font>') # use HTML format for custom color