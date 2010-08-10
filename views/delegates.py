from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TaggedDelegate(QItemDelegate):
    def __init__(self, parent = None):
        super(TaggedDelegate, self).__init__(parent)
    
    def createEditor(self, parent, option, index):
        label = QLabel("Ok.")
        label.setStyleSheet("Color: red")
        return label