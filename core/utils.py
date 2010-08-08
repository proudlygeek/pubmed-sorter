import re, sys, getopt, time

__version__="0.1.3"

#tempo di inizio
t0 = time.clock()

#Creazione del dizionario dei mesi (SiglaMese -> NumeroMese) per il sorting	
mesi = dict(zip(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',None], range(1,14)))
    
#Compilazione della espressione regolare per la validazione degli autori (DA COMPLETARE!)
authorsRegEx = re.compile(r'^(\w+ [A-Z]{1,2})$')
    
#Compilazione della espressione regolare per la validazione delle date di pubblicazione
dateRegEx = re.compile("(\d{4})(.+?)?;")

#Ricerca le possibili date valide (Formato "dddd ccc") all'interno di una lista
#@returns Intero anno, Stringa mese
def findPubDate(lista):
    for item in lista:
        date = dateRegEx.search(item)
        if date:
            return date.group(1), date.group(2)

#Metodo per l'ordinamento (by Alex Martelli, Google.Inc & Me, povero diavolo)
def descyear_ascauth(atup):
    year = int(atup[0][1][0])
    month = atup[0][1][1]
    if month:
        month = month.split(None, 1)[0][:3]
        if not re.search(r'^\w{3}$', month, re.S|re.M) or month not in mesi.keys():
            month = None
    #print year
    #print month
    firstAuthor = atup[0][2]
    #print firstAuthor
    return -year, firstAuthor

def descyear_descmonth_ascauth(atup):
    year = int(atup[0][1][0])
    month = atup[0][1][1]
    if month:
        month = month.split(None, 1)[0][:3]
        if not re.search(r'^\w{3}$', month, re.S|re.M) or month not in mesi.keys():
            month = None
    #print year
    #print month
    firstAuthor = atup[0][2]
    #print firstAuthor 
    return -year, -mesi[month], firstAuthor
    
#Scrive i risultati ordinati in un file
def printOutput(sortedList, outputFile):
    output = open(outputFile,"w")
    for line in sortedList:
        string = "%s PMID: %s\n\n\n" % (line[1][1], line[1][2])
        output.write(string)
    
    output.close()
    print("######")
    print("Output:\t%s generato con successo (%d record processati in %.3f secondi)" % (outputFile, len(sortedList), time.clock()-t0))
    print("######")
    
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

def loadFile(inputFile):
    #Apertura del file txt contenente i record PubMed da ordinare
    try:
        f = open(inputFile,"r").read().replace("\n"," ")
    except IOError as ex:
        print "Errore durante l'apertura del file: %s" % ex 
    
    #Ottiene una lista di record che soddisfano la RegEx all'int
    biglist = re.findall(r'(\d+): (.+?) PMID: (\d{7,8})', f, re.M | re.S)
    return biglist

def main(argv):
    if not argv:
        usage()
        sys.exit()


    inputFile = None
    outputFile = None
    sortMonth = False
    #Controllo dei paramatri passati
    try:
        opts, args = getopt.getopt(argv,"Mhi:o:",["MonthSort","help","input=","output="])
    except getopt.GetoptError,err:
        print str(err)
        usage()
        sys.exit(2)
    inputFile = None
    outputFile = None
    
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
        else:
            assert False, "Opzione non specificata"
            
    if outputFile == None:
        outputFile = "sorted-"+inputFile
    
    #Carica il file 
    loadFile(outputFile)

    #Estrapola i dati in varie liste:
    #numeri
    numberList = [line[0] for line in biglist]
    
    #autori
    authorList = [re.split("\s?,\s?", re.split(r"\s?\.\s?",line[1])[0]) for line in biglist]
    
    #Journal
    
    journalList = [re.split(r"\s?\.\s?",line[1])[2] for line in biglist]
    
    #data pubblicazione (chiave secondaria sort)
    dateList = [findPubDate(re.split(r"\s?\.\s?",line[1])) for line in biglist]
    
    #titolo pubblicazione
    titleList = [re.split(r"\s?\.\s?",line[1])[1] for line in biglist]
    
    #primo autore (chiave primaria sort)
    #firstAuthorList = [authorList[x][len(authorList[x]) - 1] for x in range(len(authorList))]
    firstAuthorList = [authorList[x][0] for x in range(len(authorList))]
    
    #id_pubmed
    idList = [line[2] for line in biglist]
    
    #lista sezione
    sectionList = [re.split(r"\s?\;\s?", re.split(r"\s?\.\s?", line[1])[3]) for line in biglist]
    
    
    #Compattamento chiavi di sort
    sortKeys = zip(numberList, dateList, firstAuthorList)
    
    #Creazione struttura dati completa (chiavi + dati)
    dataAndKeys = zip(sortKeys, biglist)
    
    #Sort per chiave primaria (Anno decrescente), secondaria (Mese descrescente) e terziaria (Autore crescente) 
    #sortedKeys = sorted(dataAndKeys[0], key = descyear_ascauth)
    print sortMonth
    if not sortMonth:
        result = sorted(dataAndKeys, key = descyear_ascauth)
    else:
        result = sorted(dataAndKeys, key = descyear_descmonth_ascauth)
    
    #Esporta i risultati ordinatihttp://docs.python.org/tutorial/errors.html
    printOutput(result, outputFile)
    
if __name__ == "__main__":
    main(sys.argv[1:])
