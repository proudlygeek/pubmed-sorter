import re, os, sys, getopt, time

#tempo di inizio
t0 = time.clock()

#Creazione del dizionario dei mesi (SiglaMese -> NumeroMese) per il sorting	
mesi = dict(zip(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',None], range(1,14)))
    
#Compilazione della espressione regolare per la validazione degli autori (DA COMPLETARE!)
authorsRegEx = re.compile(r'^(\w+ [A-Z]{1,2})$')
    
#Compilazione della espressione regolare per la validazione delle date di pubblicazione
dateRegEx = re.compile("(\d{4})\s?(\w\w\w)?;{0,1}")

#Ricerca le possibili date valide (Formato "dddd ccc") all'interno di una lista
#@returns Intero anno, Stringa mese
def findPubDate(lista):
    for item in lista:
        date = dateRegEx.search(item)
        if date:
            return date.group(1), date.group(2)

#Metodo per l'ordinamento (by Alex Martelli, Google.Inc & Me, povero diavolo)
def descyear_ascauth(atup):
    year = int(atup[0][0][0])
    month = atup[0][0][1]
    if month:
        month = month.split(None, 1)[0][:3]
        if not re.search(r'^\w{3}$', month, re.S|re.M) or month not in mesi.keys():
            month = None
    #print year
    #print month
    firstAuthor = atup[0][1]
    return -year, firstAuthor

def descyear_descmonth_ascauth(atup):
    year = int(atup[0][0][0])
    month = atup[0][0][1]
    if month:
        month = month.split(None, 1)[0][:3]
        if not re.search(r'^\w{3}$', month, re.S|re.M) or month not in mesi.keys():
            month = None
    #print year
    #print month
    firstAuthor = atup[0][1]
    return -year, -mesi[month], firstAuthor
    
    
#Scrive i risultati ordinati in un file
def printOutput(sortedList, outputFile):
    try:
        output = open(outputFile,"w")
        for line in sortedList:
            string = "%s PubMed PMID: %s\n\n\n" % (line[1][0], line[1][1])
            output.write(string)
        
        output.close()
        resultStr = "Output:\t%s generato con successo (%d record processati in %.3f secondi)" % (outputFile, len(sortedList), time.clock()-t0)
        print("######")
        print(resultStr)
        print("######")
        return (resultStr)
    except IOError as (errno, strerr):
        return "I/O Error (%s): %s" % (errno, strerr)
    
#Classe di exception custom (in caso di parametri nulli o errati)
def usage():
    print("# PubMed Sorter %s #" % __version__)
    print("Utilizzo: sortPub -i [inputfile] {-o [outputfile]}")
    print("Opzioni:")
    print(" -i [nomefile].txt : \tFile di testo contenente i record PubMed da ordinare")
    print(" --input=[nomefile.txt]")
    print(" -o [nomefile].txt : \tSpecifica il nome del file di output (opzionale) ")
    print(" --output=[nomefile.txt]")
    print(" -M: \t\t\tOrdina gli anni utilizzando anche i mesi (opzionale)")
    print(" --MonthSort")
    print(" -x: \t\t\tAttiva modalita' Mixed per riordinare linee numerate e non (opzionale)")
    print(" --mixedmode")

def loadFile(inputFile, mixedMode = False, guiMode = False):
    #Apertura del file txt contenente i record PubMed da ordinare
    try:
        f = open(inputFile,"r").read().replace("\n"," ").replace("\r"," ")
    except IOError as ex:
        print "Errore durante l'apertura del file: %s" % ex
    
    
    
    #Ottiene una lista di record che soddisfano la RegEx all'int
    if mixedMode:
        result = re.findall(r'\s+(.+?) PubMed\s{1,3}PMID:\s{1,3}(\d{7,8})', f, re.M | re.S)
        result = zip([re.sub(r'\d+: ', '', line[0]) for line in result], [line[1] for line in result])
    elif guiMode:
        result = re.findall(r'(\d+): (.+?) PubMed\s{1,3}PMID:\s{1,3}(\d{7,8})', f, re.M | re.S)
    else:
        result = re.findall(r'\d+: (.+?) PubMed\s{1,3}PMID:\s{1,3}(\d{7,8})', f, re.M | re.S)
    
    result = removeDuplicates(result, mixedMode, guiMode)
    
    return result

def loadFromGUI(data, files):
    #Removes tag's label and strip record number creating several lists (one for each tag
    #entered by the user) to be processed and sorted.
    #
    #@return list: Lista di stringhe contenente uno (o piu') messaggi di completamento.
    resultMsg = list()
    for f in files:
        tempList = [item[1:3] for item in data if item[3] == f]
        
        if fileExists(f):
            oldList = loadFile(f+".txt", True, False)
            tempList+=oldList
            tempList = removeDuplicates(tempList, True, False)
    
        resultMsg.append(sortPubmed(None, "%s.txt" % f, False, False, tempList))
        
    return resultMsg

def removeDuplicates(dataList, mixedMode = False, guiMode = False):
    #Removes duplicates from a list by transforming it into a dictionary and back
    #to a list using PMID as key which implicitly removes any possible record duplicate.
    #
    #@return list
    if guiMode and not mixedMode:
        keys = [line[2] for line in dataList]
        values = [(line[0], line[1]) for line in dataList]
    else:
        keys = [line[1] for line in dataList]
        values = [line[0] for line in dataList]
    
    
    dataDict = dict(zip(keys, values))
    print("Duplicati: %d; Unici: %d; Totale: %d;" % (len(dataList) - len(dataDict), len(dataDict), len(dataList)))
    result = zip(dataDict.values(), dataDict.keys())
    
    if guiMode and not mixedMode:
        result = [(item[0][0], item[0][1], item[1]) for item in result]
    
    return result

def fileExists(f):
    #Checks if file f exists into the current folder.
    #
    #@return: True if file already exists, False otherwise.
    return os.path.exists(f+".txt")

def sortPubmed(inputFile = None, outputFile = None, sortMonth =False, mixedMode=False, guiData = None):
    if outputFile == None:
        outputFile = "sorted-"+inputFile
        
    if mixedMode:
        outputFile = inputFile
    
    #Carica il file
    if not inputFile and guiData:
        biglist = guiData
    else:
        biglist = loadFile(inputFile, mixedMode)
    
    #Estrapola i dati in varie liste:
    #numeri
    #numberList = [line[0] for line in biglist]
    
    #autori
    authorList = [re.split("\s?,\s?", re.split(r"\s?\.\s?",line[0])[0]) for line in biglist]
    #Journal
    #journalList = [re.split(r"\s?\.\s?",line[1])[2] for line in biglist]
    
    #data pubblicazione (chiave secondaria sort)
    dateList = [findPubDate(re.split(r"\s?\.\s?",line[0])) for line in biglist]
    #titolo pubblicazione
    #titleList = [re.split(r"\s?\.\s?",line[1])[1] for line in biglist]
    
    #primo autore (chiave primaria sort)
    #firstAuthorList = [authorList[x][len(authorList[x]) - 1] for x in range(len(authorList))]
    firstAuthorList = [authorList[x][0] for x in range(len(authorList))]
    #id_pubmed
    idList = [line[1] for line in biglist]
    
    #lista sezione
    #sectionList = [re.split(r"\s?\;\s?", re.split(r"\s?\.\s?", line[1])[3]) for line in biglist]
    
    
    #Compattamento chiavi di sort
    sortKeys = zip(dateList, firstAuthorList)
    #Creazione struttura dati completa (chiavi + dati)
    dataAndKeys = zip(sortKeys, biglist, idList)
    
    #Sort per chiave primaria (Anno decrescente), secondaria (Mese descrescente) e terziaria (Autore crescente) 
    #sortedKeys = sorted(dataAndKeys[0], key = descyear_ascauth)
    if not sortMonth:
        result = sorted(dataAndKeys, key = descyear_ascauth)
    else:
        result = sorted(dataAndKeys, key = descyear_descmonth_ascauth)
    
    #Esporta i risultati ordinati http://docs.python.org/tutorial/errors.html
    return printOutput(result, outputFile)
    

def main(argv):
    if not argv:
        usage()
        sys.exit()
    inputFile = None
    outputFile = None
    sortMonth = False
    mixedMode = False
    #Controllo dei paramatri passati
    try:
        opts, args = getopt.getopt(argv,"xMhi:o:",["mixedmode","MonthSort","help","input=","output="])
    except getopt.GetoptError,err:
        print str(err)
        usage()
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-h","--help"):
            usage()
            sys.exit()
        elif o in ("-i","--input"):
            inputFile = a
        elif o in ("-o","--output"):
            outputFile = a
        elif o in ("-M","--MonthSort"):
            sortMonth = True
            print("SORT BY MONTH ON")
        elif o in ("-x","--mixedmode"):
            mixedMode = True
            print("MIXED MODE ON")
        else:
            assert False, "Opzione non specificata"
    
    sortPubMed(inputFile, outputFile, sortMonth, mixedMode)
            
if __name__ == "__main__":
    main(sys.argv[1:])
