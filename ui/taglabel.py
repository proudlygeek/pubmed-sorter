from PyQt4.QtCore import *
from PyQt4.QtGui import *


class TagLabel(QLabel):
    def __init__(self, text, color, parent = None):
        super(TagLabel, self).__init__(parent)
        self.setText(text)
        #Salvo il CSS dell'elemento
        self.setStyleSheet("QLabel { background-color: %s; font-size: 14pt; }" % color)
        self.defaultStyle = self.styleSheet()
        self.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/pubmedrecord"):
            self.set_bg(True)
            event.accept()
        else:
            event.reject()
    
    def dragLeaveEvent(self, event):
        self.set_bg(False)
        event.accept()
    
    def dropEvent(self, event):
        self.set_bg(False)
        print "Droppato!"
        event.accept()
    
    def enterEvent(self, event):
        #self.set_bg(True)
        #event.accept()
        pass
        
    def leaveEvent(self, event):
        #self.set_bg(False)
        #event.accept()
        pass
    
    def set_bg(self, active = False):
        if active:
            style = "background: yellow"
            self.setStyleSheet(style)
        else:
            self.setStyleSheet(self.defaultStyle)



