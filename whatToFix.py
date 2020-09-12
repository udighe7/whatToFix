import subprocess
import re
import csv

testNames = ['HelpshiftDemoiOSUIConvTests','HelpshiftDemoiOSUIFormTests']

def generateCSV(testCaseDict,testName):
    csvFileName = testName+".csv"
    with open(csvFileName, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["testSuite", "testCase", "reason", "status"])
        for testSuite in testCaseDict.keys():
            for testCase in testCaseDict[testSuite].keys():
                if len(testCaseDict[testSuite][testCase]) == 1:
                    writer.writerow([testSuite, testCase, " ", testCaseDict[testSuite][testCase][0]])
                else:
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

if __name__ == "__main__":
    main()
