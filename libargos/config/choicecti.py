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

""" Some simple Config Tree Items
"""
import logging

from libargos.config.abstractcti import AbstractCti, AbstractCtiEditor
from libargos.qt import  Qt, QtGui
from libargos.utils.misc import NOT_SPECIFIED


logger = logging.getLogger(__name__)

# Use setIndexWidget()?
 


class ChoiceCti(AbstractCti):
    """ Config Tree Item to store a choice between strings.
    """
    def __init__(self, nodeName, data=NOT_SPECIFIED, defaultData=0, choices=None, userData=None):
        """ Constructor.
        
            The data and defaultData properties are used to store the currentIndex.
            choices must be a list of string.
                    
            For the (other) parameters see the AbstractCti constructor documentation.
        """
        super(ChoiceCti, self).__init__(nodeName, data=data, defaultData=defaultData)
        self.choices = [] if choices is None else choices
        self.userData = [] if userData is None else userData
        assert len(self.userData) == 0 or len(self.userData) == len(self.choices), "size mismatch"
        
    
    def _enforceDataType(self, data):
        """ Converts to int so that this CTI always stores that type. 
        """
        return int(data)

    
    @property
    def configValue(self):
        if self.userData:
            return self.userData[self.data]
        else:
            return self.choices[self.data]
         

    @property
    def displayValue(self):
        """ Returns the string representation of data for use in the tree view. 
        """
        return str(self.choices[self.data])
        

    @property
    def displayDefaultValue(self):
        """ Returns the string representation of data for use in the tree view. 
        """
        return str(self.choices[self.defaultData])        
        
            
    @property
    def debugInfo(self):
        """ Returns the string with debugging information
        """
        return repr(self.choices)
    
    def createEditor(self, delegate, parent, option):
        """ Creates a ChoiceCtiEditor. 
            For the parameters see the AbstractCti constructor documentation.
        """
        return ChoiceCtiEditor(self, delegate, parent=parent) 
    
    
        
class ChoiceCtiEditor(AbstractCtiEditor):
    """ A CtiEditor which contains a QCombobox for editing ChoiceCti objects. 
    """
    def __init__(self, cti, delegate, parent=None):
        """ See the AbstractCtiEditor for more info on the parameters 
        """
        super(ChoiceCtiEditor, self).__init__(cti, delegate, parent=parent)
        
        comboBox = QtGui.QComboBox()
        comboBox.addItems(cti.choices)
        for idx, userDatum in enumerate(cti.userData):
            comboBox.setItemData(idx, userDatum, role=Qt.UserRole)
        
        comboBox.activated.connect(self.commitAndClose)
        
        self.comboBox = self.addSubEditor(comboBox, isFocusProxy=True)


    def finalize(self):
        """ Is called when the editor is closed. Disconnect signals.
        """
        self.comboBox.activated.disconnect(self.commitAndClose)
        super(ChoiceCtiEditor, self).finalize()   
        
    
    def setData(self, data):
        """ Provides the main editor widget with a data to manipulate.
        """
        if False and self.cti.userData:
            idx = self.cti.userData.index(data)
            logger.debug("setData: data={} -> idx = {}".format(data, idx))
        else:
            idx = data
        self.comboBox.setCurrentIndex(idx)    

        
    def getData(self):
        """ Gets data from the editor widget.
        """
        idx = self.comboBox.currentIndex()
        if False and self.cti.userData:
            return self.cti.userData[idx]
        else:
            return idx
    
    