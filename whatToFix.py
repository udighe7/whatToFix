import subprocess

def validateLogFiles(listOfLogFiles):
    testNames = ['HelpshiftDemoiOSUIConvTests','HelpshiftDemoiOSUIFormTests']
    validatedLogFiles = []
    for logFile in listOfLogFiles:
        for testName in testNames:
            if not logFile.find(testName) == -1:
                validatedLogFiles.append(logFile)
                break
    return validatedLogFiles

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
    validatedLogFiles = validateLogFiles(listOfLogFiles)
    if(len(validatedLogFiles) == 0):
        print("\nERROR: No log file found !\n")

if __name__ == "__main__":
    main()
