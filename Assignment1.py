# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 20:04:37 2021

@author: franc
"""

import os
import string
import time
from nltk.stem.porter import *
stemmer = PorterStemmer()
translator=str.maketrans('','',string.punctuation)

directory='E:\Courses\CI Info Retrival\HillaryEmails\HillaryEmails'

os.chdir(directory)
blockSize=100000
#print(fileListing(directory))
#readFile('E:\Courses\CI Info Retrival\HillaryEmails\HillaryEmails\1.txt')
#print(len(tokenize(1,readFile('E:\Courses\CI Info Retrival\HillaryEmails\HillaryEmails\\1.txt'))))
#tokenPair=tokenize(1,readFile('E:\Courses\CI Info Retrival\HillaryEmails\HillaryEmails\\1.txt'))
#print(stemming(tokenPair))
#fileList=fileListing(directory)
#print(fileList)
#file=readFile(fileList[1])
#print(file[0])
#writeTerm(fileList,'test.txt')
#for file in fileList:

def maxPair(blockSize):
    return blockSize/12

def resultsDirectory(directory):
    return directory+'\Results'

resultsDir=resultsDirectory(directory)

def fileListing(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return files

def readFile(file):
    with open(file, encoding='UTF-8') as f:
        read_data=f.read()
    return read_data

def tokenize(docID,data):
    tokenList=list(set(data.split()))
    tokenPair=list(zip(tokenList, [docID]*len(tokenList)))
    return tokenPair

def stemming(tokenPair):
    stemmed=[]
    for pair in tokenPair:
        term=pair[0].translate(translator).lower()
        if term.isnumeric() or term=='':
            continue
        stemmed.append(tuple([stemmer.stem(term),pair[1]]))
    result=list(set(stemmed))
    return result

def writeTerm(data, file):
    with open(file, 'a+', encoding='UTF-8') as f:
        f.write('\n'.join('%s,%s' % x for x in data))
        f.write('\n')
    return

def readTerm(file):
    with open(file, encoding='UTF-8') as f:
        read_data=[i.split(',') for i in f.readlines()] # read as list of 2-component list
    for term in read_data:                              # normalize list terms into string,int tuple
        term[1]=int(term[1].replace('\n',''))
    result=[tuple(i) for i in read_data]
    return result

def readFromFile(fileHandler, size):
    read_data=[i.split(',') for i in fileHandler.readlines(size)]   #limit content read to size parameter
    for term in read_data:
        term[1]=int(term[1].replace('\n',''))
    result=[tuple(i) for i in read_data]
    if result==[]:
        return ['EOF']
    return result

def docParse(directory, blockSize):                     # parse all documents in the direcotry
    maxBlock=maxPair(blockSize)
    fileList=fileListing(directory)
    termDocPair=[]
    blockNo=0
    for file in fileList:
        if len(termDocPair) >= maxBlock:
            writeTerm(termDocPair, resultsDir+'\\block' + str(blockNo) + '.txt')
            termDocPair=[]
            blockNo+=1
        docID=int(file.split('.')[0])
        text=readFile(file)
        termPair=stemming(tokenize(docID, text))
        termDocPair.extend(termPair)
    writeTerm(termDocPair, resultsDir+'\\block' + str(blockNo) + '.txt')
    return

def blockSort(file):
    terms=readTerm(file)
    terms.sort()
    writeTerm(terms, file[:-4] + 'sorted.txt')
    return
    
def mergeBlock(fileList):
    fileHandlerList=[] 
    maxLen=maxPair(blockSize)
    #blockList=[]
    for file in fileList:
        f=open(file, encoding='UTF-8')
        fileHandlerList.append(f)                   #get the list of file handlers
    blockLen=int(blockSize/len(fileList))
    tempList=[]
    tempSortedList=[]
    for handler in fileHandlerList:
        tempList.append(readFromFile(handler, blockLen))        #create the unsorted list, take equal elements from each block
    readCount=0
    writeCount=0
    while tempList !=[]:
        minimum=min(tempList)
        index=tempList.index(minimum)
        tempSortedList.append(tempList[index].pop(0))           #find the smallest term-docID pair and pop it into the sorted list
        for item in tempList:
            if item==[]:                                        #once all extracted elements from a block is popped into sorted list, get another batch of elements from that block
                readCount+=1
                index=tempList.index(item)
                item.extend(readFromFile(fileHandlerList[index], blockLen))
                if item==['EOF']:                               #once all elements of a block is extracted, remove the block from the unsorted list
                    tempList.pop(index)
                    fileHandlerList.pop(index)
        if len(tempSortedList)>=maxLen:                         #write sorted list to file, limited by max size of sorted list allowed based on block size
            writeTerm(tempSortedList, 'finalTerms.txt')
            tempSortedList=[]
            writeCount+=1
    writeTerm(tempSortedList, 'finalTerms.txt')
    print('read:' + str(readCount) + '   write:' + str(writeCount))
    return

def main(directory, blockSize):
    start = time.process_time()
    docParse(directory, blockSize)                              #Parse, normalized token pair written into files
    doneParse = time.process_time()
    os.chdir(resultsDir)
    blockList=fileListing(resultsDir)
    for block in blockList:
        before = time.process_time()                            #Sort the blocks internally
        blockSort(block)
        after = time.process_time()
        print('sorted 1 block for' + str(after - before))
    sortedBlockList=[item for item in fileListing(resultsDir) if item not in blockList]
    doneBlock = time.process_time()
    mergeBlock(sortedBlockList)                                 #external merge sort
    doneMerge = time.process_time()
    print('parsing and indexing took ' + str(doneParse-start) + '   merging took ' + str(doneMerge-doneBlock))
    return
    
main(directory,blockSize)

#docParse(directory,blockSize)
#blockSort('E:\Courses\CI Info Retrival\HillaryEmails\HillaryEmails\Results\\block0.txt')
#f=open('E:\Courses\CI Info Retrival\HillaryEmails\HillaryEmails\Results\\block4.txt', encoding='UTF-8')
#print(readFromFile(f, blockSize))
#print(readFromFile(f, blockSize))
#print(readTerm('E:\Courses\CI Info Retrival\HillaryEmails\HillaryEmails\Results\\test1')[0])
'''
os.chdir(resultsDir)
blockList=fileListing(resultsDir)
sortedBlockList=['block0sorted.txt','block1sorted.txt','block0sorted.txt']
print(sortedBlockList)
mergeBlock(sortedBlockList)
os.chdir(resultsDir)
sortedBlockList=['block0sorted.txt','block1sorted.txt','block2sorted.txt','block3sorted.txt','block4sorted.txt']
mergeBlock(sortedBlockList)

tempSortedList = []
tempList = [[('12docx', 10), ('3sourc', 10), ('4g', 10), ('a', 10), ('abdelhakim', 10), ('about', 10), ('abu', 10), ('access', 10), ('accord', 10), ('across', 10), ('act', 10), ('ad', 10), ('add', 10), ('addressess', 10), ('admit', 10), ('advantag', 10), ('advisor', 10), ('afghanistan', 10), ('after', 10), ('against', 10), ('agre', 10), ('agreement', 10), ('aid', 10), ('aim', 10), ('al', 10), ('all', 10), ('alsharia', 10), ('also', 10), ('ambassador', 10), ('among', 10), ('an', 10), ('and', 10), ('andor', 10), ('angri', 10), ('ani', 10), ('anniversari', 10), ('ansar', 10), ('anyth', 10), ('approach', 10), ('approxim', 10), ('are', 10), ('arm', 10), ('armi', 10), ('arrest', 10), ('as', 10), ('assault', 10), ('at', 10), ('atmospher', 10), ('attach', 10), ('attack', 10), ('b6', 10), ('base', 10), ('be', 10), ('becaus', 10), ('been', 10)], [('1970', 5031), ('1990', 5031), ('1clay', 5031), ('2day', 5031), ('a', 5031), ('abandon', 5031), ('abdic', 5031), ('about', 5031), ('abysm', 5031), ('access', 5031), ('accid', 5031), ('account', 5031), ('actor', 5031), ('adjust', 5031), ('administ', 5031), ('administr', 5031), ('advanc', 5031), ('advantag', 5031), ('advoc', 5031), ('afford', 5031), ('aftershock', 5031), ('against', 5031), ('agenc', 5031), ('agenda', 5031), ('ago', 5031), ('agrarian', 5031), ('agreement', 5031), ('agricultur', 5031), ('agroindustri', 5031), ('aid', 5031), ('alex', 5031), ('all', 5031), ('alon', 5031), ('alreadi', 5031), ('also', 5031), ('alter', 5031), ('alterpress', 5031), ('am', 5031), ('america', 5031), ('among', 5031), ('an', 5031), ('and', 5031), ('ani', 5031)]]
while tempList !=[]:
    tempList.sort()
    #print(tempList[0])
    #print(tempList[1])
    tempSortedList.append(tempList[0].pop(0))
    print(tempList)
    print(tempSortedList)
'''
