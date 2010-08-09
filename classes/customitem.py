from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CustomItem(QListView):
    def __init__(self, parent = None, type = QListWidgetItem.UserType):
        super(CustomItem, self).__init__(parent)