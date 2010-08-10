from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pickle


class TagLabel(QLabel):
    def __init__(self, text, color, parent = None):
        super(TagLabel, self).__init__(parent)
        #Un tag possiede testo e colore
        self.tagColor = color
        self.setText(text)
        #Salvo il CSS dell'elemento
        self.setStyleSheet("QLabel { background-color: %s; font-size: 14pt; }" % self.tagColor)
        self.defaultStyle = self.styleSheet()
        self.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.setAcceptDrops(True)
        #print self.parent().parent().parent().parent()
        #Connessioni
        self.connect(self, SIGNAL("dropAccepted(PyQt_PyObject)"), self.parent().parent().parent().parent().dummyMsg)

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
        #print ("Nome tag: %s" %self.text())
        #print ("Colore tag: %s" % self.tagColor)
        data = event.mimeData()
        bstream = data.retrieveData("application/pubmedrecord", QVariant.ByteArray)
        #print bstream.isValid()
        selected = pickle.loads(bstream.toByteArray())
        #print selected
        event.accept()
        self.emit(SIGNAL("dropAccepted(PyQt_PyObject)"), (selected, str(self.text()), str(self.tagColor)))
        
        
    
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
            style = "QLabel {background: yellow; font-size: 14pt;}"
            self.setStyleSheet(style)
        else:
            self.setStyleSheet(self.defaultStyle)



