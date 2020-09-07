import subprocess

def getListOfLogFiles():
    searchInDirectory = '~/Library/Developer/xcode/DerivedData'
    fileName = "StandardOutputAndStandardError.txt"
    cmd = "find "+searchInDirectory+" -name "+"'"+fileName+"'"
    listOfLogFiles = [line for line in subprocess.check_output(cmd, shell=True).splitlines()]
    return listOfLogFiles

def main():
    listOfLogFiles = getListOfLogFiles()

if __name__ == "__main__":
    main()
