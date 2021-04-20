import re
import sys
from error import ErrorHandler

class Frames:
    def __init__(self):
        self.globalFrame = {}
        self.frameStack = []
        self.tmpFrame = None
        self.type = False 

    def createTmpFrame(self):
        self.tmpFrame = {}

    # Function returns value and type of given argument
    def getValueAndType(self, arg):
        if not re.match('^(int|bool|string|type|label|nil)$', arg['type']):
            frame, name = arg['value'].split('@', 1)
            frameSearch = self.getFrame(frame)
            if frameSearch == 'UNDEFINED':
                ErrorHandler.errorExit(55, "Invalid frame")
            if name in frameSearch:
                if frameSearch[name]['value'] is None and frameSearch[name]['type'] is None and not self.type:
                    ErrorHandler.errorExit(56, "Missing value")
                value = frameSearch[name]['value']
                type = frameSearch[name]['type']
                return value, type
            else: ErrorHandler.errorExit(54, "Invalid variable")
        else: return arg['value'], arg['type']

    def getFrame(self, frame):
        if frame == 'GF':
            return self.globalFrame
        elif frame == 'TF':
            if self.tmpFrame is not None:
                return self.tmpFrame
            else: return 'UNDEFINED'
        else:
            if len(self.frameStack) > 0:
                return self.frameStack[len(self.frameStack) - 1]
            else: return 'UNDEFINED'

    # Set variable in given frame
    def setvar(self, arg, type, value):
        frame, name = arg['value'].split('@', 1)
        frameInsert = self.getFrame(frame)
        if frameInsert == 'UNDEFINED':
            ErrorHandler.errorExit(55, "Invalid frame")
        if name in frameInsert:
            frameInsert[name]['value'] = value
            frameInsert[name]['type'] = type
        else: 
            ErrorHandler.errorExit(54, "Invalid variable")