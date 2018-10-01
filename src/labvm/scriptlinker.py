#!/usr/bin/env python3

import os
import sys

class ScriptLinker:

    _program : str
    _debug : bool
    
    def __init__(self, inputProgram : str, debug=False):
        self._debug = debug
        self._program = inputProgram

    def link(self) -> str:
        splitted = self._program.split("\n")

        # remove comments and strip all lines
        toremove = []
        for i, line in enumerate(splitted):
            if "//" in line:
                if "//" == line.strip()[0:2]:
                    self._debugP("Found comment in line " + str(i) + " gonna remove")
                    toremove.append(i)
                else:
                    self._debugP("Found comment in line " + str(i))
                    splitted[i] = str(line[0:line.find("//")])
            if line.strip() == "":
                self._debugP("Found empty line at " + str(i))
                toremove.append(i)
            splitted[i] = splitted[i].strip()
        count = 0
        for i in toremove:
            del splitted[i - count]
            count = count + 1

        # collect all labels and their future line number
        symbols = {}
        toremove = []
        for i, line in enumerate(splitted):
            if line[-1] == ":":
                self._debugP("Found symbol: " + line + " in line " + str(i))
                if line in symbols:
                    print("Error: Symbol", line, "duplicate")
                    sys.exit(1)
                symbols[line] = i - len(symbols)
                toremove.append(i)
        self._debugP("Found " + str(len(symbols)) + " labels: " + str(symbols))
        count = 0
        for i in toremove:
            del splitted[i - count]
            count = count + 1

        # resolve all symbols
        for i, line in enumerate(splitted):
            if line + ":" in symbols:
                self._debugP("Found symbol: " + line)
                splitted[i] = str(symbols[line + ":"] + 1)  # +1 bc lines begin with 1 in the vm

        self._debugP(str(splitted))
        return "\n".join(splitted)

    def _debugP(self, message : str):
        if(self._debug):
            print(message)
                    



# cli interface
if len(sys.argv) < 2 or len(sys.argv) > 4 or (len(sys.argv) > 2 and sys.argv[2] != "-o"):
    print("Usage:", sys.argv[0], "FILE [-o outputName]")
    sys.exit(1)

if sys.argv[1] in ["-h", "--help"]:
    print(
            """
            labVM Script Linker.
            Usage: ./scriptlinker.py FILE [-o outputName]
            Resolves symbols and comments from a labvm script
            """
        )
    sys.exit(1)

inputName = sys.argv[1]

inputFile = open(inputName, "r")

sl = ScriptLinker(inputFile.read(), True)
inputFile.close()

if(len(sys.argv) == 2):
    if "." in inputName:
        outputName = inputName.split(".")[0] + ".labe"
    else:
        ouputName = inputName + ".labe"
else:
    outputName = sys.argv[3]
i = 1
outputNameChecked = outputName
while os.path.isfile(outputNameChecked):
    outputNameChecked = outputName + str(i)
    i = i + 1

outputFile = open(outputNameChecked, "w+")
outputFile.write(sl.link())
outputFile.close()

sys.exit(0)
