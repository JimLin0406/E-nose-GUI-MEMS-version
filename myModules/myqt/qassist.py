#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################
# Assistant tool for PySide2
#
# Author: Kevin Tung (Yen-Chiang, Tung) <kevin.wtmh@gmail.com>
#
# Organization: National Cheng Kung University, BME, WTMH Lab, 2022, Taiwan
#
# Edit Year: 2022
#
# # License: BSD 3 clause
#######################################################
from pandas import DataFrame, concat
from PySide2.QtWidgets import QTableWidget

class QAssist:
    def get_table_content(table:QTableWidget, howdrop:str='all'):
        """ Get the table content

        Parameters
        ----------
        table: QTableWidget

        howdrop : {'any', 'all', None}, default 'all'
            Determine if row or column is removed from DataFrame, 
            when we have at least one NA or all NA.
            - 'any': If any NA values are present, drop that row or column.
            - 'all': If all values are NA, drop that row or column.
            - None: Nor drop any row

        Returns
        ----------
        table_content: DataFrame
        """

        try:
            headers = [table.horizontalHeaderItem(col).text() 
                        for col in range(table.columnCount())]
        except:
            headers = [f'Col {col}' for col in range(table.columnCount())]

        content = DataFrame()
        for row in range(table.rowCount()):
            row_data = list()
            for col in range(table.columnCount()):
                item = table.item(row,col)
                text = item.text() if item is not None else None
                row_data.append(text)
            content = concat([content, DataFrame(row_data).T], axis=0)
        content.columns = headers
        content = content.dropna(how=howdrop) if howdrop is not None else content
        return content