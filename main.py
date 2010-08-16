import sys
import os.path
import platform
import qrc_resources
import operator
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from script.utils import loadFile
from ui.ui import *
from views.dragtable import DragTable
from ui.taglabel import TagLabel
from classes.customlist import CustomList
from script.utils import loadFromGUI
from script.utils import fileExists

__version__="0.2.4"
__license__="LGPL VERSION 3.0"

class MainWindow(QMainWindow):
    def __init__(self, Parent = None):
        super(MainWindow, self).__init__()
        
        #Variabile file
        self.fileInput = None
        self.listTag = None
        #Inizializzazione finestra principale
        self.setWindowTitle("PubMed Sorter")
        self.setWindowIcon(QIcon(":/icon.png"))
        self.resize(200, 200)
        self.center()
        #Creazione lista centrale
        loadLabel = QLabel ("<b> Carica un documento per iniziare </b>")
        self.setCentralWidget(loadLabel)

        #Status Bar
        self.status =self.statusBar()
        self.status.setSizeGripEnabled(True)
        self.status.showMessage("Nessun documento caricato.",5000)
        
        #Azioni
        fileOpenAction = self.createAction("&Apri file...", self.fileOpen, QKeySequence.Open, "fileopen", "Carica un documento PubMed")
        self.fileCloseAction = self.createAction("&Chiudi file", self.fileClose, QKeySequence.Close, "fileclose", "Chiudi il documento attuale")
        #disattivato inizialmente
        self.fileCloseAction.setEnabled(False)
        fileQuitAction = self.createAction("&Esci", self.close, "Ctrl+Q", None, "Esci dal programma")
        helpAboutAction = self.createAction("&About...", self.helpAbout, "Ctrl+Alt+A",None,"Informazioni sul software")
        
        #Barra dei menu
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        self.addActions(fileMenu, (fileOpenAction, self.fileCloseAction, None, fileQuitAction))
        helpMenu = menu.addMenu("&Help")
        helpMenu.addAction(helpAboutAction)
        
        
    def createDock(self):
        if not self.listTag:
            #Creazione lista tag laterale (area dock)
            taglistDockWidget = QDockWidget("Lista Tag:",self)
            taglistDockWidget.setObjectName("taglistDockWidget")
            taglistDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
            self.listTag = ListTagWidget(self)
            taglistDockWidget.setWidget(self.listTag)
            #buttontest = TagLabel("Test", "red", self)
            #taglistDockWidget.setWidget(buttontest)
            self.addDockWidget(Qt.LeftDockWidgetArea, taglistDockWidget)
    
    #Metodo per la creazione rapida di azioni   
    def createAction(self, text, slot = None, shortcut = None, icon = None, tip = None, checkable = False, signal ="triggered()"):
        action = QAction(text,self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    
    #Metodo per la aggiunta rapida di azioni a Menu' e Toolbar
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    
    def fileOpen(self):
        self.fileInput = QFileDialog.getOpenFileName(self, "Apri Documento...", "%s" % os.getcwd(),"File di testo (*.txt)")
        if os.path.isfile(self.fileInput):
            dataToLoad = loadFile(self.fileInput, False, True)
            #Aggiungo il campo per i tag alla struttura dati (conversione a lista)
            self.dataWithTagsField = [list(line) for line in dataToLoad]
            
            for line in self.dataWithTagsField:
                #Inizializza i tag con il simbolo "meno"
                line.append('-')
                
            #converti i primi valori in interi (per sort colonna)
            for line in self.dataWithTagsField:
                line[0] = int(line[0])
                
            self.fullScreen()
            self.centralWidget = CentralWidget(self.dataWithTagsField, self)
            self.setCentralWidget(self.centralWidget)
            self.createDock()
            self.fileCloseAction.setEnabled(True)
            
            #Ricarica dizionario tag
            for item in [self.listTag.listWidget.itemWidget(self.listTag.listWidget.item(x)) for x in range(self.listTag.listWidget.count())]:
                item.reConnect()
            
            self.status.showMessage("%s caricato." % self.fileInput,5000)        
            
    def fileClose(self):
        self.fileInput = None
        self.dataWithTagsField = None
        self.centralWidget.close()
        self.fileCloseAction.setEnabled(False)
        self.setCentralWidget(QLabel("<b> Carica un documento per iniziare </b>").setAlignment(Qt.AlignHCenter | Qt.AlignVCenter))
    
    def helpAbout(self):
        QMessageBox.about(self, "About PubMed Sorter",
                """<b>PubMed Sorter</b> v %s
                <p>Copyright &copy; 2010 Gianluca Bargelli 
                All right reserved.
                <p>Released under license %s.</p>
                <p>This application can be used to perform <a href = "http://www.ncbi.nlm.nih.gov/pubmed">PubMed</a> record filtering and sorting from plain PubMed txt format.</p>
                <p>Python %s - Qt %s - PyQt %s on %s</p>""" % (__version__, __license__, platform.python_version(), QT_VERSION_STR,
                PYQT_VERSION_STR, platform.system()))
    
    
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    
    def fullScreen(self):
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width(), screen.height())
        
    def generateFiles(self):
        tagsList = list()
        for item in self.dataWithTagsField:
            tagsList.append(item[3])
        
        tagsList = list(set(tagsList))
        
        nfiles = len(tagsList)
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Conferma Generazione File")
        
        existsMsg = """<p style = "font-size: 9pt">
                    (Il file <b style = "color: red">esiste</b>;
                    I record verranno <b>integrati</b> e <b>ordinati</b>)</p>"""
        if nfiles > 1:
            fileStr = """Verranno scritti <b>%d</b> files:
                      <ul>""" % nfiles
            for tag in tagsList:
                if tag == '-':
                    fileStr+="""<li><p>notag.txt</p></li>"""
                    if fileExists(tag):
                        fileStr+=(existsMsg)
                else:
                    fileStr+="""<li><p>%s.txt</p></li>""" % tag
                    if fileExists(tag):
                        fileStr+=(existsMsg)
            fileStr+="""</ul>"""
        else:
            fileStr = """Verra' generato <b>un solo</b> file:"""
            
            if tagsList[0] == '-':
                fileStr+="""<p>NoTag.txt</p>"""
                if fileExists(tagsList[0]):
                        fileStr+=(existsMsg)
            else:
                fileStr+="""<p>%s.txt</p>""" % tagsList[0]
                if fileExists(tagsList[0]):
                        fileStr+=(existsMsg)
                
        fileStr+="""<b>Vuoi continuare?</b>"""
            
        msgBox.setText(fileStr)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setIcon(QMessageBox.Question)
        result = msgBox.exec_()
        
        if result == QMessageBox.Yes:
            msgList = loadFromGUI(self.dataWithTagsField, tagsList)
            msgBoxResult = QMessageBox()
            bodyText ="""<p>Risultato generazione file:</p>
                            <ul>"""
            for msg in msgList:
                bodyText+="""<li><p>%s</p></li>""" % msg
            bodyText+="""</ul>"""
            msgBoxResult.setWindowTitle("Risultato")
            msgBoxResult.setText(bodyText)
            msgBoxResult.setStandardButtons(QMessageBox.Ok)
            msgBoxResult.setIcon(QMessageBox.Information)
            msgBoxResult.exec_()
        elif result == QMessageBox.No:
            return
        
class ListTagWidget(QWidget):
        def __init__(self, parent = None):
            super(ListTagWidget, self).__init__(parent)
            #Creazione componenti
            addButton = QPushButton("&Aggiungi Tag...")
            self.editButton = QPushButton("&Modifica Tag...")
            self.removeButton = QPushButton("&Rimuovi Tag")
            self.editButton.setEnabled(False)
            self.removeButton.setEnabled(False)
            self.listWidget = CustomList(self)
            #Creazione Layout
            layout = QGridLayout(self)
            layout.addWidget(self.listWidget, 1, 1, 1, 1)
            layout.addWidget(addButton, 2, 1)
            layout.addWidget(self.editButton, 3, 1)
            layout.addWidget(self.removeButton, 4, 1)
            self.setLayout(layout)
            self.setMaximumWidth(200)
            self.adjustSize()
            #Connessioni
            self.connect(addButton, SIGNAL("clicked()"), self.addTag)
            self.connect(self.editButton, SIGNAL("clicked()"), self.editTag)
            self.connect(self.removeButton, SIGNAL("clicked()"), self.delTag)
            self.connect(self.listWidget, SIGNAL("currentRowChanged(int)"), self.enableEditDel)
        
        def addTag(self):
            dialog = AddTagDlg(self.listWidget, self)
            dialog.show()
            if dialog.exec_():
                self.refreshSizeItems()
                
        def editTag(self):
            dialog = EditTagDlg(self.listWidget, self)
            dialog.show()
            if dialog.exec_():
                pass
                
        def delTag(self):
            item = self.listWidget.itemWidget(self.listWidget.currentItem()).text()
            
            if item:
                msgBox = QMessageBox(self)
                msgBox.setText("Sei sicuro di voler eliminare il tag ""%s""?" % item)
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setWindowTitle("Rimuovi Tag")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                result = msgBox.exec_()
                
                if result == QMessageBox.Ok:
                    self.listWidget.takeItem(self.listWidget.currentRow())
                    self.refreshSizeItems()
                
                elif result == QMessageBox.Cancel:
                    return
        
        def enableEditDel(self, index):
            if index != -1:
                self.editButton.setEnabled(True)
                self.removeButton.setEnabled(True)
            else:
                self.editButton.setEnabled(False)
                self.removeButton.setEnabled(False)

        def refreshSizeItems(self):
            size = self.listWidget.size()
            
            for item in [self.listWidget.item(x) for x in range(self.listWidget.count())]:
                item.setSizeHint(QSize(item.sizeHint().width(), size.height()/(self.listWidget.count()) ))
                #item.setAcceptDrops(True)
                #item.setDropIndicatorShown(True)

class CentralWidget(QWidget):
    def __init__(self, data, parent=None):
        super(CentralWidget, self).__init__(parent)
        self.data = data
        self.tableList = self.createTable()
    
    #Creazione della tabella
    def createTable(self):
        tableView = DragTable()
        generateButton = QPushButton("&Genera File(s)")
        layout = QVBoxLayout()
        layout.addWidget(tableView)
        layout.addWidget(generateButton)
        self.setLayout(layout)
        header = ['#','Dati','PMID','Tag']
        tableModel = pubmedTableList(self.data, header, self)
        tableView.setModel(tableModel)
        hh = tableView.horizontalHeader()
        hh.resizeSection(1, super(CentralWidget, self).width()+100)
        #hh.setResizeMode(QHeaderView.Stretch)
        hh.swapSections(1,3)
        hh.swapSections(1,2)
        hh.setStretchLastSection(True)
        tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.resizeColumnToContents(0)
        tableView.resizeColumnToContents(2)
        tableView.resizeColumnToContents(3)
        #Connessioni
        self.connect(generateButton, SIGNAL("clicked()"), self.parent().generateFiles)
        return tableView
        

#Classe Tabella Abstract (Mapping diretto tra struttura dati e tabella)
class pubmedTableList(QAbstractTableModel):
    def __init__(self, dataIn, dataHeader, Parent = None):
        super(pubmedTableList, self).__init__()
        self.dataHeader = dataHeader
        self.publication = dataIn
    #Ritorna il numero di righe ovvero il numero di record PubMed
    def rowCount(self, Parent):
        return len(self.publication)
    
    #Ritorna il numero di colonne ovvero il numero dei campi di un singolo record
    def columnCount(self, Parent):
        return len(self.publication[0])
        
    #Mapping struttura dati <-> tabella
    def data(self, index, role):
        #Nel caso di visualizzazione ritorna l'oggetto per riga e colonna
        if role == Qt.DisplayRole:
            item = self.publication[index.row()][index.column()]
            return item
        #Nel caso di drag and drop ritorna direttamente la riga contenente il record
        elif role == Qt.UserRole:
            item = self.publication[index.row()][0]
            return item
        #Ruolo del delegato
        elif role == "ColorRow":
            item = self.publication[index.row()][3]
            return item
        
        elif role == Qt.TextAlignmentRole and index.column() == 3:
            return (Qt.AlignRight | Qt.AlignVCenter)
            
        return QVariant()
        
    def setData(self, index, value, role):
        if role == "NoRow":
            #Essendo una selezione multipla ho un insieme da scorrere
            for element in index:
                self.publication[element][3] = value
                
            self.emit(SIGNAL("dataChanged()"))
            return True
        else:
            return False
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.dataHeader[col])
        return QVariant()
        
    def supportedDragActions(self):
        return (Qt.MoveAction | Qt.CopyAction)
    
    def flags(self, index):
        if index.isValid():
            return (Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable )
    
    def sort(self, Ncol, order):
        #Ordina la tabella dato il numero di colonna e l'ordinamento
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        if order == Qt.AscendingOrder:
            self.publication = sorted(self.publication, key=operator.itemgetter(Ncol))        
        elif order == Qt.DescendingOrder:
            self.publication.reverse()
        self.emit(SIGNAL("layoutChanged()"))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())