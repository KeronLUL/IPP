import argparse
import sys
from xmlParser import XMLParser
from frames import Frames
from core import Interpret

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
    try:
        inputFile, sourceFile = argument_parser()
    except SystemExit:
        exit(10)

    xml = XMLParser(sourceFile)
    try:
        instList, labels = xml.checkXML()
    except IndexError:
        exit(31)

    interpret = Interpret(instList, labels)
    interpret.run(inputFile)
 
if __name__ == '__main__':
    main()
    
