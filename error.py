import sys

class ErrorHandler:
    def __init__(self):
        pass

    def errorExit(error, message):
        print(message, file=sys.stderr)
        sys.exit(error)
