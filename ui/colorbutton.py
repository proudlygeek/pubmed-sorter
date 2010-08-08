from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ColorButton(QPushButton):
    def __init__(self, parent=None):
        super(ColorButton, self).__init__(parent)
        self.setText("")
    
    def setColor(self, color):
        self.setStyleSheet("ColorButton {background-color: %s }" % color.name())