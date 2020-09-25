# WhatToFix

A utility written in python for triaging UI automation test logs for iOS in a better way.

## Why do we need it?

* In Xcode when we go to **Report Navigator** we get the history of your build, run, debug, continuous integration, and source control tasks etc 
[report navigator](https://github.com/udighe7/whatToFix/blob/feature/images/reportNavigator.png)

* But, the thing here is that if you have a large number of UI or Unit test running under a particular scheme -
    * Now, let's say you added a new feature into your app.
    * And, suddenly many of your UI or Unit tests starts to fail.
    * In this situation you don't want to go through each and every test failure in Xcode and try to fix them one by one.
    * Also, there might be some test which you plan to fix later.
    * Moreover if there are more that one test target you might be willing to focus on some targets only.

* In this situation one of the most effecient way could be to start solving most common issues to increase % of tests passed under a particular target.

* And thats where this utility come in!

## What it can do?

* WhatToFix will go through all the test logs generated in `/../Library/Developer/Xcode/DerivedData/..` directory and will do couple of things -

    1. It will create a CSV file for each and every target with following format -
        | testSuite | testCase | reason | status |
        | ---------- | ---------- | -------- | ------- |
        |                |                |             |            |
        |                |                |             |            |
        
    2. It will generate a HTML file which would list down the most common reasons for failure in descending order for each target mentioned in `whatToFix.py` . And that's not it -
        * It would also tell number of test failing due to the particular reason.
        * % of success rate affected by this failure.
        * And list of of the test cases that are failing.
        [whatToFix.html](https://github.com/udighe7/whatToFix/blob/feature/images/whatToFix.png)
        
## How to get started?

1. Once you have downloaded the repo, open `whatToFix.py` file.
2. Search for a global variable named as `testNames`. Add the names of test target which you want to analyze in that list.
3. Install `pandas` module for python or create a virtual env and install the module in it.
4. If you have create virtual env, active it.
5. Run cmd `python whatToFix.py`.
6. Refer to the CSV files generated for all test targets. The CSV files would be named after test targets.
7. Refer `whatToFix.html` for test cases grouped with common reason for failures for each target.
