import argparse
import sys
import re
from xmlParser import XMLParser
from frames import Frames

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='Source file')
    parser.add_argument('--input', help='Input file')
    args = parser.parse_args()

    if not args.source and not args.input:
        exit(10)
    
    if not args.source:
        args.source = sys.stdin
    if not args.input:
        args.input = sys.stdin
    inputFile = args.input
    sourceFile = args.source

    return inputFile, sourceFile


def main():
    inputFile, sourceFile = argument_parser()
    xml = XMLParser(sourceFile)
    instList = xml.checkXML()
    globalframe = {}
    for x in range(len(instList)):
        if instList[x][1][0] == 'DEFVAR':
            name = instList[x][1][1].split("@", 1)[1]
            if name not in globalframe:
                globalframe[x] = {name}

        if instList[x][1][0] == 'MOVE':
            name = instList[x][1][1].split("@", 1)[1]
            
    print(globalframe)       
if __name__ == '__main__':
    main()
    
