# IPP 2021
# error.py
# Author: Karel Norek, xnorek01

import sys

# Class that handles errors
class ErrorHandler:
    def __init__(self):
        pass

    def errorExit(error, message):
        print(message, file=sys.stderr)
        sys.exit(error)
