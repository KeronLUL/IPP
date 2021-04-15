import re

class Frames:
    def __init__(self):
        self.globalFrame = {}
        self.frameStack = list()
        self.tmpFrame = None
        self.type = False 

    def createTmpFrame(self):
        self.tmpFrame = {}

    def getValueAndType(self, arg):
        if not re.match('^(int|bool|string|type|label|nil)$', arg['type']):
            frame, name = arg['value'].split('@', 1)
            frameSearch = self.getFrame(frame)
            if frameSearch == 'UNDEFINED':
                exit(55)
            if name in frameSearch:
                if frameSearch[name]['value'] is None and frameSearch[name]['type'] is None and not self.type:
                    exit(56)
                value = frameSearch[name]['value']
                type = frameSearch[name]['type']
                return value, type
            else: exit(54)
        else: return arg['value'], arg['type']

    def getFrame(self, frame):
        if frame == 'GF':
            return self.globalFrame
        elif frame == 'TF':
            if self.tmpFrame is not None:
                return self.tmpFrame
            else: return 'UNDEFINED'
        elif frame == 'LF':
            if len(self.frameStack) > 0:
                return self.frameStack[len(self.frameStack) - 1]
            else: return 'UNDEFINED'

    def setvar(self, arg, type, value):
        frame, name = arg['value'].split('@', 1)
        frameInsert = self.getFrame(frame)
        if frameInsert == 'UNDEFINED':
            exit(55)
        if name in frameInsert:
            frameInsert[name]['value'] = value
            frameInsert[name]['type'] = type
        else: 
            exit(54)
        
    def defvar(self, arg):
        frame, name = arg['value'].split('@', 1)
        frameInsert = self.getFrame(frame)
        if frameInsert == 'UNDEFINED':
            exit(55)
        if name not in frameInsert:
            frameInsert[name] = {'type': None, 'value': None}
        else:
            exit(52)