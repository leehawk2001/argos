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

""" Version and other info for this program
"""
import logging, platform

from libargos.qt import getQApplicationInstance, QtCore, QtGui, printAllWidgets
from libargos.utils.misc import string_to_identifier
from libargos.widgets.mainwindow import MainWindow


logger = logging.getLogger(__name__)

class ArgosApplication(object):
    """ The application singleton which holds global stat
    """
    def __init__(self):
        """ Constructor
        """
        self._profile = "Panoptes"
        self._mainWindows = []
        self._settingsSaved = False  # boolean to prevent saving settings twice
        
        # Call getQApplicationInstance() so that the users can call libargos.browse without 
        # having to call it themselves.
        self._qApplication = getQApplicationInstance()
        
        #self.readViewSettings(reset=resetSettings)
        
        self.qApplication.lastWindowClosed.connect(self.quit) 

        
    @property
    def qApplication(self):
        """ Returns the QApplication object
        """
        return self._qApplication

        
    @property
    def mainWindows(self):
        """ Returns the number of MainWindows. For read-only purposes only.
        """
        return self._mainWindows

    
    @property
    def profile(self):
        """ Persistent settings are associated to a profile. This allows users to save the
            program state for several usage profiles.
            Profile settings are case insensitive. 
        """
        return self._profile
    
        
    def _groupNameForWindow(self, windowNr):
        """ Returns the group name (for use in the QSettings) given a window number.
        """
        return "window-{:02d}".format(windowNr)


    def readViewSettings(self, reset=False): # TODO: read profile?
        """ Reads the persistent program settings
        """ 
        return False # TODO remove
        settings = QtCore.QSettings()
        logger.debug("Reading settings from: {}".format(settings.fileName()))
        
        profileGroupName = string_to_identifier(self.profile)
        
        if reset:
            logger.debug("Resetting profile settings: {}".format(profileGroupName))
            settings.remove(profileGroupName)
    
        # Instantiate windows from groups            
        settings.beginGroup(profileGroupName)
        try:
            for windowGroupName in settings.childGroups():
                if windowGroupName.startswith('window'):
                    settings.beginGroup(windowGroupName)
                    try:
                        mainWindow = self.createMainWindow()
                        mainWindow.readViewSettings(settings)
                        #QtCore.QPoint(20 * self._instanceNr, 20 * self._instanceNr)))
                    finally:
                        settings.endGroup()
        finally:
            settings.endGroup()
            

    def writeViewSettings(self):
        """ Writes the view settings to the persistent store
        """
        return False # TODO remove
        assert self._settingsSaved == False, "settings already saved"
        self._settingsSaved = True                        
                 
        settings = QtCore.QSettings()  
        logger.debug("Writing settings to: {}".format(settings.fileName()))

        profileGroupName = string_to_identifier(self.profile)
        settings.remove(profileGroupName) # start with a clean slate

        assert self.mainWindows, "no main windows found"
        settings.beginGroup(profileGroupName)
        try:
            for winNr, mainWindow in enumerate(self.mainWindows):
                windowGroupName = self._groupNameForWindow(winNr)
                settings.beginGroup(windowGroupName)
                try:
                    mainWindow.writeViewSettings(settings)
                finally:
                    settings.endGroup()
        finally:
            settings.endGroup()
                        
                        
    def writeViewSettingsIfNeeded(self):
        """ Writes the persistent settings of this profile is this is the last window and
            the settings have not yet been saved.
        """
        return False
        if not self._settingsSaved and len(self.mainWindows) <= 1:
            self.writeViewSettings()
            
            
    def createMainWindow(self, fileNames = tuple()):
        """ Creates and shows a new MainWindow.
            All fileNames in the fileNames list are opened
            The **kwargs are passed on to the MainWindow constructor.
        """
        # Assumes qt.getQApplicationInstance() has been executed.
        mainWindow = MainWindow(self)
        self.mainWindows.append(mainWindow)
        
        mainWindow.openFiles(fileNames=fileNames) # TODO: make possible without main window
        
        mainWindow.show()
        if platform.system() == 'Darwin':
            mainWindow.raise_()
        return mainWindow
    
    
    def removeMainWindow(self, mainWindow):
        """ Removes the mainWindow from the list of windows. Saves the settings
        """
        logger.debug("removeMainWindow called")
        self.mainWindows.remove(mainWindow)  # TODO: enable

    
    def closeAllWindows(self):
        """ Closes all windows. Save windows state to persistent settings before closing them.
        """
        self.writeViewSettings()
        
        logger.debug("quitApplication: Closing all windows")
        self.qApplication.closeAllWindows()
        

            
    def quit(self):
        """ Called when the application quits (when the last window is closed)
            Saves persistent settings when this wasn't done already.
        """
        logger.debug("ArgosApplication.quit called")
        
        #assert len(self.mainWindows) == 0, \
        #    "Still {} windows present at application quit!".format(len(self.mainWindows))
            
        app = QtGui.QApplication.instance() # TODO: use _qApplication
        assert app is self.qApplication, "sanity check"
        
        from libargos.qt import printChildren
        printChildren(self.qApplication)        
        printAllWidgets(self.qApplication, ofType=MainWindow)
        self.qApplication.quit()


    def execute(self):
        """ Executes all main windows by starting the Qt main application
        """  
        logger.info("Starting Argos...")
        exitCode = self.qApplication.exec_()
        logger.info("Argos finished with exit code: {}".format(exitCode))
        printAllWidgets(self.qApplication)
        return exitCode
    
            


        
        
    
def createArgosApplicationFunction():
    """ Closure to create the ArgosApplication singleton
    """
    globApp = ArgosApplication()
    
    def accessArgosApplication():
        return globApp
    
    return accessArgosApplication

# This is actually a function definition, not a constant
#pylint: disable=C0103

getArgosApplication = createArgosApplicationFunction()
getArgosApplication.__doc__ = "Function that returns the ArgosApplication singleton"

