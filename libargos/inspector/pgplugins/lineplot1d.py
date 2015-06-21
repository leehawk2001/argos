# -*- coding: utf-8 -*-

# This file is part of Argos.
# 
# Argos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Argos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Argos. If not, see <http://www.gnu.org/licenses/>.

""" PyQtGraph 1D line plot
"""
from __future__ import division, print_function

import logging
import pyqtgraph as pg

from libargos.qt import Qt, QtGui
from libargos.info import DEBUGGING
from libargos.config.emptycti import EmptyCti
from libargos.config.boolcti import BoolCti
from libargos.config.choicecti import ChoiceCti
from libargos.config.colorcti import ColorCti
from libargos.config.floatcti import FloatCti
#from libargos.config.intcti import IntCti
from libargos.inspector.abstract import AbstractInspector
from libargos.utils.cls import array_has_real_numbers

logger = logging.getLogger(__name__)

PEN_STYLES = [Qt.SolidLine, Qt.DashLine, Qt.DotLine, Qt.DashDotLine, Qt.DashDotDotLine]

class PgLinePlot1d(AbstractInspector):
    """ Inspector that contains a PyQtGraph 1-dimensional line plot
    """
    
    def __init__(self, collector, parent=None):
        """ Constructor. See AbstractInspector constructor for parameters.
        """
        super(PgLinePlot1d, self).__init__(collector, parent=parent)
        
        self.plotWidget = pg.PlotWidget(name='1d_line_plot_#{}'.format(self.windowNumber),
                                        title='', enableMenu=False) 
        self.contentsLayout.addWidget(self.plotWidget)
        
        
    def finalize(self):
        """ Is called before destruction. Can be used to clean-up resources
        """
        logger.debug("Finalizing: {}".format(self))
        self.plotWidget.close()
                
        
    @classmethod
    def axesNames(cls):
        """ The names of the axes that this inspector visualizes.
            See the parent class documentation for a more detailed explanation.
        """
        return tuple(['X-axis'])


    @classmethod        
    def createConfig(cls):
        """ Creates a config tree item (CTI) hierarchy containing default children.
        """
        rootItem = EmptyCti('inspector')
        rootItem.insertChild(ColorCti('pen color', defaultData="#3F8E3A"))
        
        # A pen line width of zero indicates a cosmetic pen. This means that the pen width is 
        # always drawn one pixel wide, independent of the transformation set on the painter.
        # Note that line widths other than 1 may be slow when anti aliasing is on.
        rootItem.insertChild(FloatCti('pen width', defaultData=1.0, 
                                      minValue=0.0, maxValue=100, stepSize=1, decimals=1))
        
        rootItem.insertChild(ChoiceCti('pen style', defaultData=0, 
            choices=['solid line', 'dashed line', 'dotted line', 
                     'dash-dot line', 'dash-dot-dot line']))
        
        logAxesItem = rootItem.insertChild(EmptyCti('logarithmic'))
        logAxesItem.insertChild(BoolCti('X-axis', defaultData=False))
        logAxesItem.insertChild(BoolCti('Y-axis', defaultData=False))
        
        gridItem = rootItem.insertChild(EmptyCti('grid'))
        gridItem.insertChild(BoolCti('X-axis', defaultData=True))
        gridItem.insertChild(BoolCti('Y-axis', defaultData=True))
        gridItem.insertChild(FloatCti('alpha', defaultData=0.25, 
                                      minValue=0.0, maxValue=1.0, stepSize=0.01, decimals=2))
        return rootItem
    
                
    def _initContents(self):
        """ Draws the inspector widget when no input is available.
            Creates an empty plot.
        """
        self.plotWidget.clear()
        #self.plotWidget.showAxis('right')
        self.plotWidget.setLogMode(x=self.configValue('logarithmic/X-axis'), 
                                   y=self.configValue('logarithmic/Y-axis'))

        self.plotWidget.showGrid(x=self.configValue('grid/X-axis'), 
                                 y=self.configValue('grid/Y-axis'), 
                                 alpha=self.configValue('grid/alpha'))

        self.plotDataItem = self.plotWidget.plot()
        
        pen = QtGui.QPen()
        pen.setCosmetic(True)
        pen.setColor(self.configValue('pen color'))
        pen.setWidthF(self.configValue('pen width'))
        pen.setStyle(PEN_STYLES[self.configValue('pen style')])
        self.plotDataItem.setPen(pen)


    def _updateRti(self):
        """ Draws the RTI
        """
        ylabel = self.collector.dependentDimensionName()
        depUnit = self.collector.dependentDimensionUnit()
        if depUnit:
            ylabel += ' ({})'.format(depUnit)
        self.plotWidget.setLabel('left', ylabel)

        xlabel = self.collector.independentDimensionNames()[0]
        indepUnit = self.collector.independentDimensionUnits()[0]
        if indepUnit:
            xlabel += ' ({})'.format(indepUnit)
        self.plotWidget.setLabel('bottom', xlabel)
        
        rti = self.collector.rti
        rtiProps = {'rtiPath': rti.nodePath, 'slices': self.collector.getSlicesString()}
        cfgTitle = "{rtiPath} {slices}"
        try:
            title = cfgTitle.format(**rtiProps) 
        except Exception:
            logger.warn("Unable set title {!r} from: {}".format(cfgTitle, rtiProps))
            title = 'Unable to determine the title'
            
        self.plotWidget.setTitle(title)
            
        slicedArray = self.collector.getSlicedArray()
        
        if slicedArray is None or not array_has_real_numbers(slicedArray):
            self.plotDataItem.clear()
            if not DEBUGGING:
                raise ValueError("No data available or it does not contain real numbers")
        else:
            self.plotDataItem.setData(slicedArray)
            
        