#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################
# Author: Kevin Tung (NCKU.BME.2021)
#
# Organization: Biomedical Engineering, National Cheng Kung University, Taiwan
#
# Edit Year: 2021
#######################################################
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QFont, QBrush
from PySide2.QtCharts import QtCharts

class QPieChart(QtCharts.QChart):
    def __init__(self, parent=None):
        super().__init__()

        self.pieSeries = QtCharts.QPieSeries()
        self.pieSeries.setHoleSize(0.2)
        self.pieSeries.setPieSize(0.7)
        self.pieSeries.setLabelsVisible(True)

        self.addSeries(self.pieSeries)
        self.createDefaultAxes()
        self.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        self.legend().setVisible(True)
        self.legend().setAlignment(Qt.AlignRight)

        self.update(labels=None, quantity=None)
        
        # self.setAnimationOptions(QtCharts.QChart.NoAnimation)
        self.setBackgroundVisible(False)
        # self.setTheme(QtCharts.QChart.ChartThemeDark)
        # self.setTheme(QtCharts.QChart.ChartThemeBlueCerulean)

        # add to QChartView to view
        self.chartView = QtCharts.QChartView(self)
        self.chartView.setContentsMargins(0, 0, 0, 0)
     
    def update(self, labels=None, quantity=None):
        self.pieSeries.clear()
        if labels is not None:
            for i in range(len(labels)):
                pieSlice = QtCharts.QPieSlice()
                pieSlice.setValue(quantity[i])
                self.pieSeries.append(pieSlice)

            for i, slice in enumerate(self.pieSeries.slices()):
                slice.setLabel(labels[i])
                self.legend().markers(self.pieSeries)[i].setLabel("%s: %.1f%%" % (labels[i], slice.percentage()*100))
                font = QFont()
                font.setPointSize(10)
                slice.setLabelFont(font)
                slice.setLabelColor(QColor(255, 255, 255))
                self.legend().markers(self.pieSeries)[i].setFont(font)
                self.legend().markers(self.pieSeries)[i].setLabelBrush(QBrush(QColor(255, 255, 255)))
        else:
            pieSlice = QtCharts.QPieSlice()
            pieSlice.setValue(1)
            pieSlice.setLabel("%s: %.1f%%" % ('None', 0))
            pieSlice.setColor(QColor('gray'))
            self.pieSeries.append(pieSlice)
            
        self.pieSeries.setLabelsVisible(True)
        self.legend().setVisible(True)
        self.legend().setAlignment(Qt.AlignRight)
        self.setAnimationOptions(QtCharts.QChart.SeriesAnimations)