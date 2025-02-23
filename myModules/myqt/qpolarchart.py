#!venv/bin/python3
# -*- coding: utf-8 -*-
#
# Author: Kevin F. Tung (Yen-Chiang, Tung)
# Organization: National Cheng Kung University, BME, WTMH Lab, 2021, Taiwan
# Copyright © 2021 NCKU WTMH E-Nose Team - All Right Reserved.
# References: https://www.qter.org/portal.php?mod=view&aid=6802
#             https://doc-snapshots.qt.io/qtforpython/PySide2/QtCharts/QChart.html

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from PySide2.QtCore import Qt, QPointF
from PySide2.QtGui import QColor, QPen
from PySide2.QtCharts import QtCharts

class QPolarChart(QtCharts.QPolarChart):
    def __init__(self, channels: int=16, reverse: bool=False):
        super().__init__()

        self.channels = channels
        self.reverse = reverse
        
        data = np.linspace(0, channels*10, channels, endpoint=False)  # for draw the radar chart skeleton
        dataLength = len(data)

        # get the initial angles and radials
        self.angles = np.linspace(0, 360, dataLength, endpoint=False)
        self.angles = np.concatenate((self.angles, [360]))
        self.radials = self._getRadials(data)
 
        # set the data coordinates
        self.lineSeries = QtCharts.QLineSeries()
        [self.lineSeries.append(QPointF(*coordinates)) for coordinates in zip(self.angles, self.radials)]
        self.lineSeries.setName("Channel: Delta")
        self.addSeries(self.lineSeries)

        # set the angular axis and labels
        self.angularAxis = QtCharts.QCategoryAxis()
        self.angularAxis.setLabelsPosition(QtCharts.QCategoryAxis.AxisLabelsPositionOnValue)
        self.angularAxis.setRange(0, 360)
        [self.angularAxis.append(f"CH {i+1}", angle) for i, angle in enumerate(self.angles) if i!=dataLength]
        self.addAxis(self.angularAxis, QtCharts.QPolarChart.PolarOrientationAngular)

        # set the radial axis and labels
        radialTicks = np.linspace(np.min(self.radials), np.max(self.radials), 8)
        radialLabels = np.flip(radialTicks) if self.reverse else radialTicks
        radialTicks = list(map(lambda x: int(f'{x:.0f}'), radialTicks))
        radialLabels = list(map(lambda x: f'{x:.0f}', radialLabels))
        self.radialAxis = QtCharts.QCategoryAxis()
        self.radialAxis.setLabelsPosition(QtCharts.QCategoryAxis.AxisLabelsPositionOnValue)
        self.radialAxis.setRange(np.min(radialTicks), np.max(radialTicks))
        [self.radialAxis.append(label, radial) for label, radial in zip(radialLabels, radialTicks)]
        self.addAxis(self.radialAxis, QtCharts.QPolarChart.PolarOrientationRadial)

        # attaches the axis specified by axis to the series.
        self.lineSeries.attachAxis(self.radialAxis)
        self.lineSeries.attachAxis(self.angularAxis)

        # set chart theme
        self.setBackgroundVisible(False)
        # self.setTheme(QtCharts.QChart.ChartThemeDark)
        self.setTheme(QtCharts.QChart.ChartThemeBlueCerulean)

        # set color
        self.lineSeries.setPen(QPen(QColor('#FFC93C'), 3, Qt.SolidLine))

        self.angularAxis.setLinePen(QPen(QColor('#8e84a6'), 3, Qt.SolidLine))
        self.angularAxis.setLabelsColor(QColor('#8e84a6'))
        self.angularAxis.setGridLineColor(QColor('#8e84a6'))
        
        # self.radialAxis.setLinePen(QPen(QColor('#40487f'), 2, Qt.SolidLine))
        # self.radialAxis.setLabelsColor(QColor('#40487f'))
        self.radialAxis.setGridLinePen(QPen(QColor('#8e84a6'), 3, Qt.SolidLine))

        # add to QChartView to view
        self.chartView = QtCharts.QChartView(self)
        self.chartView.setContentsMargins(0, 0, 0, 0)

    def _getRadials(self, update_data: np.array=None) -> np.array:
        if self.reverse:
            intercept = update_data-np.min(update_data)
            radials = np.max(update_data)-intercept
            radials = np.concatenate((radials, [radials[0]]))
        else:
            radials = np.concatenate((update_data, [update_data[0]]))
        return radials

    def _updateRadialAxis(self, update_data: np.array=None, ticksNumber:int=8):
        # check if all elements in update_data are the same, 
        # if they are, then set an initial value instead
        if np.all(update_data == update_data[0]):
            update_data = np.linspace(0, self.channels*10, self.channels, endpoint=False)

        # need to detach radial axis before remove radial axis from previous chart
        self.lineSeries.detachAxis(self.radialAxis)
        self.removeAxis(self.radialAxis)

        # calculate the radial range
        radial_interval = np.ceil((np.max(update_data)-np.min(update_data))/(ticksNumber-1))
        radial_interval = 1 if radial_interval==0 else radial_interval

        radialTicks =[]
        radialAccumulation = np.min(update_data)
        for i in range(ticksNumber):
            radialTicks.append(radialAccumulation)
            radialAccumulation = radialAccumulation + radial_interval

        radialLabels = np.flip(radialTicks) if self.reverse else radialTicks
    
        self.radialAxis = QtCharts.QCategoryAxis()
        self.radialAxis.setLabelsPosition(QtCharts.QCategoryAxis.AxisLabelsPositionOnValue)
        self.radialAxis.setRange(np.min(radialTicks), np.max(radialTicks))
        self.radialAxis.setStartValue(np.min(radialTicks))
        [self.radialAxis.append(f'{label:.0f}', radial) for label, radial in zip(radialLabels, radialTicks)]
        self.addAxis(self.radialAxis, QtCharts.QPolarChart.PolarOrientationRadial)
        self.radialAxis.setGridLinePen(QPen(QColor('#8e84a6'), 3, Qt.SolidLine))

        # attach radial axis again after update the radial axis
        self.lineSeries.attachAxis(self.radialAxis)

    def setReverse(self, reverse: bool=False):
        self.reverse = reverse
       
    def update(self, update_data: np.array=None):
        is_valid_data = bool(update_data is not None)
        update_data = np.array(update_data).reshape(-1)
        if is_valid_data:
            self.lineSeries.clear()
            self.radials = self._getRadials(update_data)
            [self.lineSeries.append(QPointF(*coordinates)) for coordinates in zip(self.angles, self.radials)]
            self._updateRadialAxis(update_data)

        self.setVisible(is_valid_data)
     
    def setVisible(self, visible: bool=True):
        self.lineSeries.setVisible(visible)
        self.radialAxis.setLabelsVisible(visible)