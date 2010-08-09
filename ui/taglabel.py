from PyQt4.QtCore import *
from PyQt4.QtGui import *


class TagLabel(QLabel):
    def __init__(self, text, color, parent = None):
        super(TagLabel, self).__init__(parent)
        self.setText(text)
        #Salvo il CSS dell'elemento
        self.defaultStyle = self.setStyleSheet("QLabel { background-color: %s; font-size: 14pt; }" % color)
        self.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.setAcceptDrops(True)
        
    def dragEventEnter(self, event):
        if event.mimeData().hasFormat("application/pubmedrecord"):
            self.set_bg(True)
            event.accept()
        else:
            event.reject()
        print "Drag Queen!"
    
    def dropEvent(self, event):
        print "Droppato!"
        event.accept()
    
    def set_bg(self, active = False):
        if active:
            style = "background: yellow"
        else:
            style = self.defaultStyle
        self.setStyleSheet(val)



