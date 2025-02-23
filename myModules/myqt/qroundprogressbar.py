#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################
# Author: Kevin Tung (NCKU.BME.2021)
#
# Organization: Biomedical Engineering, National Cheng Kung University, Taiwan
#
# Description: Custom style of QRoundProgressBar
#######################################################
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtGui import QColor, QPalette, QFont
from myModules.myqt import QRoundProgressBarBase

class QRoundProgressBar(QRoundProgressBarBase):
    def __init__(self):
        super().__init__()
        
        self.fontSize = 16
        font = QFont()
        font.setFamily("Segoe UI")
        font.setBold(True)
        self.setFont(font)

        self.setDataPenWidth(1)
        self.setOutlinePenWidth(1)
        self.setDonutThicknessRatio(0.75)
        self.setDecimals(1)
        self.setFormat('None')

        self.setNullPosition(90)
        self.setBarStyle(self.StyleDonut)

        self.setDataColors(None)

        self.setRange(0, 100)
        self.setValue(0)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)

        palette = self.palette()
        palette.setColor(QPalette.AlternateBase, QColor('#1b2043'))
        palette.setColor(QPalette.Shadow, QColor(9, 177, 177))
        palette.setColor(QPalette.Highlight, QColor(255, 170, 0))
        palette.setColor(QPalette.Text, QColor(9, 177, 177))
        self.setPalette(palette)

    def drawText(self, p, innerRect, innerRadius, value):
        if not self.format:
            return

        text = self.valueToText(value)

        f = self.font()
        if not self.fontSize:
            fontSize = innerRadius * 1.8 / len(text)
        else:
            fontSize = self.fontSize
        f.setPixelSize(fontSize)
        p.setFont(f)
        
        textRect = innerRect
        p.setPen(self.palette().text().color())
        p.drawText(textRect, Qt.AlignCenter, text)

    def update_bar(self, title=None, value=None, unit=None):
        if title and unit is not None:
            self.setFormat(f"{title}\n%s {unit}")
        elif title is not None:
            self.setFormat(f"{title}\n%s")
  
        if value is not None:
            self.setValue(value)