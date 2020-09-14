import subprocess
import re
import csv
import os
import pandas as pd
import collections

testNames = ['HelpshiftDemoiOSUIConvTests','HelpshiftDemoiOSUIFormTests']

def getEndingHTMLString():
    endingHTMLString = "</body></html>"
    return endingHTMLString

def getHTMLStringFromCSV(csvFile):
    df = pd.read_csv(csvFile)
    failureReasons = df.groupby('reason').groups.keys()
    htmlstring = ""
    if len(failureReasons):
        dictToCount = {}
        for reason in failureReasons:
            dictToCount[reason] = df[df['reason'] == reason]['testCase'].nunique()
        od = collections.OrderedDict(sorted(dictToCount.items(), key=lambda x: x[1], reverse=True))
        htmlstring = "<br><h2 text-transform: uppercase>"+csvFile+"</h2>"
        htmlstring += "<ul>"
        for reason in od.keys():
            htmlstring += "<li><input type='checkbox' checked><i></i><h2>"
            htmlstring += reason
            htmlstring += "</h2><p>"
            testCases = df[df['reason'] == reason]['testCase'].values.tolist()
            for testCase in testCases:
                htmlstring += testCase
                htmlstring += "<br>"
            htmlstring += "</p></li>"
        htmlstring += "</ul>"
    return htmlstring

def getMiddleHTMLString():
    csvFiles = [f for f in os.listdir(os.getcwd()) if f.endswith('.csv')]
    middleHTMLString = ""
    for csvFile in csvFiles:
        middleHTMLString += getHTMLStringFromCSV(csvFile)
    return middleHTMLString

def getStartingHTMLString():
    startingHTMLString = "<!DOCTYPE html><html lang='en' ><head><meta charset='UTF-8'><title>WHAT-TO-FIX</title><link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/normalize/5.0.0/normalize.min.css'><link rel='stylesheet' href='https://fonts.googleapis.com/css?family=Titillium+Web:300,700,300italic'><link rel='stylesheet' href='./style.css'><script src='https://cdnjs.cloudflare.com/ajax/libs/prefixfree/1.0.7/prefixfree.min.js'></script></head><body><h1>What-To-Fix</h1>"
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

def generateDictsForFile(file,testCaseDict):
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

def createCSVData(validatedLogFilesDict):
    for testName in validatedLogFilesDict.keys():
        testCaseDict = {}
        for logFile in validatedLogFilesDict[testName]:
            testCaseDict = generateDictsForFile(logFile,testCaseDict)
        generateCSV(testCaseDict,testName)

def validateLogFiles(listOfLogFiles):
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

def getListOfLogFiles():
    searchInDirectory = '~/Library/Developer/xcode/DerivedData'
    fileName = "StandardOutputAndStandardError.txt"
    cmd = "find "+searchInDirectory+" -name "+"'"+fileName+"'"
    listOfLogFiles = [line for line in subprocess.check_output(cmd, shell=True).splitlines()]
    return listOfLogFiles

def main():
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
