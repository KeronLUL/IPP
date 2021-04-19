#!/usr/bin/env python3.8

import argparse
import sys
from xmlParser import XMLParser
from frames import Frames
from core import Interpret
from error import ErrorHandler

# Argument check
def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='Source file')
    parser.add_argument('--input', help='Input file')
    args = parser.parse_args()

    if not args.source and not args.input:
        sys.exit(10)
    
    if not args.source:
        args.source = sys.stdin
    if not args.input:
        args.input = sys.stdin
    inputFile = args.input
    sourceFile = args.source

    return inputFile, sourceFile

def main():
    try:
        inputFile, sourceFile = argument_parser()
    except SystemExit:
        if len(sys.argv) > 1 and sys.argv[1] == '--help':
            sys.exit(0)
        else: ErrorHandler.errorExit(10, "Invalid arguments")

    xml = XMLParser(sourceFile)
    try:
        instList, labels = xml.checkXML()
    except IndexError:
        ErrorHandler.errorExit(32, "Invalid XML structure")

    interpret = Interpret(instList, labels)
    interpret.run(inputFile)
    sys.exit(0)

if __name__ == '__main__':
    main()
    