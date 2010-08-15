from PyQt4.QtCore import *
from PyQt4.QtGui import *
import cPickle
import pickle
import os
from delegates import TaggedDelegate

class DragTable(QTableView):
    def __init__(self, parent = None):
        super(DragTable, self).__init__(parent)
        self.setDragEnabled(True)
        self.setItemDelegateForColumn(3, TaggedDelegate(self))
        #Ordinamento numerico crescente per la colonna "#"
        self.setSortingEnabled(True)
        #self.colorDict = {0: '#ffffff', 1: '#c5c5c7', 2: '#ff0000'}
        #Dizionario dei colori  (per la colorazione del campo tag)
        self.colorDict = {}
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/pubmedrecord"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def startDrag(self, event):
        #index = self.indexAt(event.pos())
        #if not index.isValid():
        #    return
        indices = self.selectedIndexes()
        selected = set()
        
        for index in indices:
            selected.add(index.row())
        
        #selected = self.model().data(index, Qt.UserRole)
        #selected = index.row()
        #Conversione a ByteStream
        bstream = cPickle.dumps(selected)
        mimeData = QMimeData()
        mimeData.setData("application/pubmedrecord", bstream)
        #animazione drag
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        #pixmap = QPixmap(400, 400)
        #pixmap.fill(Qt.transparent)
        pixmap = QPixmap(":/drag.png")

        #p = QPainter(pixmap)
        #p.setRenderHint(QPainter.Antialiasing)
        #p.setBrush(Qt.white)
        #p.setBackgroundMode(Qt.TransparentMode)
        #pen = QPen(Qt.DashLine)
        #pen.setWidth(3)
        #pen.setColor(QColor("Grey"))
        #pen.setCapStyle(Qt.RoundCap)
        #p.setPen(pen)
        #rectangle = QRectF(30, 30, 100, 100)
        #p.drawRoundedRect(rectangle, 15.0, 15.0)
        #pixmap = QPixmap(":/drag.png")
        #pixmap = pixmap.scaled(QSize(100, 100))
        #pixmap = QPixmap(200, 200)
        #pixmap.fill(QColor("orange"))
        

        drag.setHotSpot(QPoint(pixmap.width()/3, pixmap.height()/3))
        drag.setPixmap(pixmap)
        result = drag.start(Qt.MoveAction)
    
    def mouseMoveEvent(self, event):
        self.startDrag(event)

    def updateData(self, item):
        self.model().setData(item[0], item[1], "NoRow")
        #Aggiorna il dizionario dei colori
        for element in item[0]:
            self.colorDict[element] = item[2]
        
        self.reset()
        self.resizeColumnToContents(3)