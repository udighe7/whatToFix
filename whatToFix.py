# -*- coding: utf-8 -*-

import subprocess
import re
import csv
import os
import pandas as pd
import collections
import sys

testNames = []
isXcode10 = True

def getEndingHTMLString():
    endingHTMLString = "</body></html>"
    return endingHTMLString

def getHTMLStringFromCSV(csvFile):
    df = pd.read_csv(csvFile)
    failureReasons = df.groupby('reason').groups.keys()
    totalTestCases = df['testCase'].nunique()
    htmlString = ""
    csvFile = csvFile[:len(csvFile)-4]
    if len(failureReasons):
        dictToCount = {}
        for reason in failureReasons:
            dictToCount[reason] = df[df['reason'] == reason]['testCase'].nunique()
        od = collections.OrderedDict(sorted(dictToCount.items(), key=lambda x: x[1], reverse=True))
        htmlString = "<br><h2>"+csvFile+"</h2><br>"
        htmlString += "<ul>"
        for reason in od.keys():
            htmlString += "<li><input type='checkbox' checked><i></i><h3>"
            htmlString += reason
            htmlString += "<br>❄️ Total tests failed : "
            htmlString += str(od[reason])
            htmlString += "<br>❄️ Affecting automation stability by : "
            percent = round(od[reason]*100.0/totalTestCases,3)
            htmlString += str(percent) + " %"
            htmlString += "</h3><p>"
            testCases = df[df['reason'] == reason]['testCase'].values.tolist()
            for testCase in testCases:
                htmlString += "🔺  "
                htmlString += testCase
                htmlString += "<br>"
            htmlString += "</p></li>"
        htmlString += "</ul>"
    return htmlString

def getMiddleHTMLString():
    csvFiles = [f for f in os.listdir(os.getcwd()) if f.endswith('.csv')]
    middleHTMLString = ""
    for csvFile in csvFiles:
        middleHTMLString += getHTMLStringFromCSV(csvFile)
    return middleHTMLString

def getStartingHTMLString():
    startingHTMLString = "<!DOCTYPE html><html lang='en' ><head><meta charset='UTF-8'><title>WHAT-TO-FIX</title><link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/normalize/5.0.0/normalize.min.css'><link rel='stylesheet' href='https://fonts.googleapis.com/css?family=Titillium+Web:300,700,300italic'><link rel='stylesheet' href='./style.css'><script src='https://cdnjs.cloudflare.com/ajax/libs/prefixfree/1.0.7/prefixfree.min.js'></script></head><body><h1>WHAT-TO-FIX 🛠</h1>"
    return startingHTMLString

def createHTMLFile():
    htmlString = getStartingHTMLString()
    htmlString += getMiddleHTMLString()
    htmlString += getEndingHTMLString()
    with open("whatToFix.html", "w") as text_file:
        text_file.write(htmlString)

def generateCSV(testCaseDict,testName):
    csvFileName = testName+".csv"
    with open(csvFileName, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["testSuite", "testCase", "reason", "status"])
        for testSuite in testCaseDict.keys():
            for testCase in testCaseDict[testSuite].keys():
                if len(testCaseDict[testSuite][testCase]) == 1:
                    writer.writerow([testSuite, testCase, "", testCaseDict[testSuite][testCase][0]])
                elif len(testCaseDict[testSuite][testCase]) == 2:
                    writer.writerow([testSuite, testCase, testCaseDict[testSuite][testCase][0], testCaseDict[testSuite][testCase][1]])

def generateDictsForFileForXcode11AndAbove(file,testCaseDict):
    print(testCaseDict)
    file = open(file,"r")
    testSuite = ""
    testCase = ""
    executingTest = False
    for line in file:
        if(not executingTest):
            startingTestCase = re.search("^Test Case '-\[(?P<test_suite>\w+) (?P<test_case>\w+)\]'.*started.",line)
            if(startingTestCase):
                testSuite = startingTestCase.group('test_suite')
                testCase = startingTestCase.group('test_case')
                executingTest = True
                if not testSuite in testCaseDict.keys():
                    testCaseDict[testSuite] = {testCase:[]}
                elif not testCase in testCaseDict[testSuite].keys():
                    testCaseDict[testSuite][testCase] = []
        else:
            failingtestCase = re.search(".* error:.*] : (?P<reason>.*)",line)
            if(failingtestCase):
                reason = failingtestCase.group("reason").rstrip()
                if len(testCaseDict[testSuite][testCase]) == 0:
                    testCaseDict[testSuite][testCase] = [reason,]
            else:
                endingTestCase = re.search("^Test Case.*]' (?P<result>\w+) .*",line)
                if(endingTestCase):
                    if testSuite in line and testCase in line:
                        if (not "passed" in testCaseDict[testSuite][testCase] and not "failed" in testCaseDict[testSuite][testCase]):
                            testCaseDict[testSuite][testCase].append(endingTestCase.group("result"))
                        executingTest = False
    return testCaseDict

def generateDictsForFileForXcode10(file,testCaseDict):
    file = open(file,"r")
    testSuite = ""
    testCase = ""
    executingTest = False
    for line in file:
        if(not executingTest):
            startingTestCase = re.search("^Test Case '-\[(?P<test_suite>\w+) (?P<test_case>\w+)\]'.*started.",line)
            if(startingTestCase):
                testSuite = startingTestCase.group('test_suite')
                testCase = startingTestCase.group('test_case')
                executingTest = True
                if not testSuite in testCaseDict.keys():
                    testCaseDict[testSuite] = {testCase:[]}
                elif not testCase in testCaseDict[testSuite].keys():
                    testCaseDict[testSuite][testCase] = []
        else:
            failingtestCase = re.search("^    t =.*Assertion Failure:.*:[0-9]+: (?P<reason>.*)",line)
            if(failingtestCase):
                reason = failingtestCase.group("reason").rstrip()
                if len(testCaseDict[testSuite][testCase]) == 0:
                    testCaseDict[testSuite][testCase] = [reason,]
            else:
                endingTestCase = re.search("^Test Case.*]' (?P<result>\w+).*",line)
                if(endingTestCase):
                    if testSuite in line and testCase in line:
                        if (not "passed" in testCaseDict[testSuite][testCase] and not "failed" in testCaseDict[testSuite][testCase]):
                            testCaseDict[testSuite][testCase].append(endingTestCase.group("result"))
                        executingTest = False
    return testCaseDict

def generateDictsForFile(file,testCaseDict):
    if isXcode10:
        return generateDictsForFileForXcode10(file,testCaseDict)
    else:
        return generateDictsForFileForXcode11AndAbove(file,testCaseDict)

def createCSVData(validatedLogFilesDict):
    for testName in validatedLogFilesDict.keys():
        testCaseDict = {}
        for logFile in validatedLogFilesDict[testName]:
            testCaseDict = generateDictsForFile(logFile,testCaseDict)
        generateCSV(testCaseDict,testName)

def validatedLogFilesForXcode11AndAbove(listOfLogFiles):
    validatedLogFilesDict = {}
    numForValidLogFiles = 0
    for file in listOfLogFiles:
        for testName in testNames:
            stringShouldBeInLogFile = "Test target "+testName
            fileHandle = open(file,"r")
            testNameFound = False
            for line in fileHandle:
                if stringShouldBeInLogFile in line:
                    if not testName in validatedLogFilesDict.keys():
                        validatedLogFilesDict[testName] = []
                    validatedLogFilesDict[testName].append(file)
                    testNameFound = True
                    numForValidLogFiles += 1
                    break
            if testNameFound:
                break
    return (validatedLogFilesDict, numForValidLogFiles)

def validatedLogFilesForXcode10(listOfLogFiles):
    validatedLogFilesDict = {}
    numForValidLogFiles = 0
    for logFile in listOfLogFiles:
        for testName in testNames:
            if not logFile.find(testName) == -1:
                if(not testName in validatedLogFilesDict.keys()):
                    validatedLogFilesDict[testName] = []
                validatedLogFilesDict[testName].append(logFile)
                numForValidLogFiles += 1
                break
    return (validatedLogFilesDict,numForValidLogFiles)

def validateLogFiles(listOfLogFiles):
    if isXcode10:
        return validatedLogFilesForXcode10(listOfLogFiles)
    else:
        return validatedLogFilesForXcode11AndAbove(listOfLogFiles)

def getPathForLogFiles():
    path = ""
    while(len(path)==0):
        path = raw_input("\nEnter the path to directory where log files are stored : ")
    return path

def getListOfLogFiles():
    searchInDirectory = '~/Library/Developer/xcode/DerivedData'
    if not isXcode10:
        searchInDirectory = getPathForLogFiles()
    fileName = "StandardOutputAndStandardError.txt"
    if not isXcode10:
        fileName = "*.txt"
    cmd = "find "+searchInDirectory+" -name "+"'"+fileName+"'"
    listOfLogFiles = [line for line in subprocess.check_output(cmd, shell=True).splitlines()]
    return listOfLogFiles

def isXcode10Used(xcodeVersion):
    versionAndSubversion = xcodeVersion.split(".")
    if not versionAndSubversion[0] == "10":
        global isXcode10
        isXcode10 = False

def main():
    if len(sys.argv) == 1:
        print("Xcode version required!")
        exit(0)
    isXcode10Used(sys.argv[1])
    listOfLogFiles = getListOfLogFiles()
    if(len(listOfLogFiles) == 0):
        print("\nERROR: No log file found !\n")
        exit(0)
    tupleForValidLogFiles = validateLogFiles(listOfLogFiles)
    if(tupleForValidLogFiles[1] == 0):
        print("\nERROR: No log file found !\n")
        exit(0)
    createCSVData(tupleForValidLogFiles[0])
    createHTMLFile()

if __name__ == "__main__":
    main()
