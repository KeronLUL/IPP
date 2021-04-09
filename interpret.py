import argparse
import sys

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
    inputFile = args.source
    sourceFile = args.input

    return inputFile, sourceFile


def main():
    inputFile, sourceFile = argument_parser()

if __name__ == "__main__":
    main()
    
