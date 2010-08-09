from PyQt4.QtCore import *
from PyQt4.QtGui import *
import cPickle
import pickle
import os

class DragTable(QTableView):
    def __init__(self, parent = None):
        super(DragTable, self).__init__(parent)
        self.setDragEnabled(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/pubmedrecord"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        
        selected = self.model().data(index, Qt.UserRole)
        #Conversione a ByteStream
        bstream = cPickle.dumps(selected)
        #print pickle.loads(bstream).data()
        mimeData = QMimeData()
        mimeData.setData("application/pubmedrecord", bstream)
        #animazione drag
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        pixmap = QPixmap(":/drag.png")
        pixmap = pixmap.scaled(QSize(100, 100))
        #pixmap = QPixmap(200, 200)
        #pixmap.fill(QColor("orange"))
        

        drag.setHotSpot(QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)
        result = drag.start(Qt.MoveAction)
    
    def mouseMoveEvent(self, event):
        self.startDrag(event)

        
        
        
        
        
        

