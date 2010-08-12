from PyQt4.QtGui import *
from PyQt4.QtCore import *
from colorbutton import ColorButton
from taglabel import TagLabel
from classes.customitem import CustomItem

class AddTagDlg(QDialog):
    def __init__(self, list, parent=None):
        super(AddTagDlg, self).__init__(parent)
        self.setModal(True)
        self.list = list
        self.color = QColor('red')
        #Creazione elementi dialog
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.colorPickerButton = ColorButton()
        self.colorPickerButton.setColor(self.color)
        labelTag = QLabel("Nome &Tag:")
        self.lineEdit = QLineEdit()
        labelTag.setBuddy(self.lineEdit)
        labelColor = QLabel("&Colore:")
        labelColor.setBuddy(self.colorPickerButton)
        #Creazione layout dialog
        grid = QGridLayout()
        grid.addWidget(labelTag, 0, 0)
        grid.addWidget(self.lineEdit, 0, 1)
        grid.addWidget(labelColor,1, 0)
        grid.addWidget(self.colorPickerButton, 1, 1)
        grid.addWidget(buttonBox, 2, 0, 1, 2)
        self.setLayout(grid)
        self.setWindowTitle("Aggiungi Tag")
        #Connessioni
        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(self.colorPickerButton, SIGNAL("clicked()"), self.chooseColorDlg)
        
    #Riscrittura per validazione Post-mortem
    def accept(self):
        item = QListWidgetItem()
        itemLabel = TagLabel(self.lineEdit.text(), self.color.name(), self)
        self.list.addItem(item)
        self.list.setItemWidget(item, itemLabel)
        QDialog.accept(self)
    
    def chooseColorDlg(self):
        dialog = QColorDialog(self)
        #Connessioni
        self.connect(dialog, SIGNAL("colorSelected(QColor)"), self.setColor)
        dialog.show()
    
    def setColor(self, color):
        self.color = color
        self.colorPickerButton.setColor(color)

class EditTagDlg(AddTagDlg):
    def __init__(self, list, parent = None):
        super(EditTagDlg, self).__init__(parent)
        #Prende il widget associato all'oggetto (QLabel)
        itemWidget = list.itemWidget(list.currentItem())
        self.setWindowTitle("Modifica Tag")
        self.setColor(QColor(itemWidget.tagColor))
        self.lineEdit.setText(itemWidget.text())
        self.lineEdit.selectAll()

