class Frames:
    def __init__(self):
        self.globalFrame = {}
        self.tmpFrame = None
        self.frameStack = list()
        self.localFrame = self.frameStack[-1]

    def createTmpFrame():
        self.tmpFrame = {}