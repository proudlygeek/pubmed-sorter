from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TaggedDelegate(QStyledItemDelegate):
    def __init__(self, parent = None):
        super(TaggedDelegate, self).__init__(parent)    
    
    def paint(self, painter, option, index):
        text = index.model().data(index, "ColorRow")
        document = QTextDocument()
        document.setDefaultFont(option.font)        
        document.setHtml(text)
        
        if text == "-":
            colorTag = QColor("White")
        else:
            colorTag = QColor(self.parent().colorDict[text])
            
        painter.save()
        painter.fillRect(option.rect, colorTag)
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()
