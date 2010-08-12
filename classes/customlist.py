from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CustomList(QListWidget):
    def __init__(self, parent = None):
        super(CustomList, self).__init__(parent)
        self.setAutoScroll(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def wheelEvent(self, event):
            print type(event)
            event.ignore()