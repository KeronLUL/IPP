import sys
import re
from frames import Frames
from error import ErrorHandler

class Interpret:
    def __init__(self, list, labels):
        self.frames = Frames()
        self.instList = list
        self.labels = labels
        self.dataStack = []
        self.stackItems = 0
        self.callStack = []
        
    # Function for arithmetic instructions
    def arithmetic(self, opcode, counter):
        value1, type1 = self.frames.getValueAndType(self.instList[counter][1].arg2)
        value2, type2 = self.frames.getValueAndType(self.instList[counter][1].arg3)

        if not(type1 == type2 and type1 == 'int'):
            ErrorHandler.errorExit(53, "Bad operand types")
        if opcode == 'ADD':
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) + int((value2))))
        elif opcode == 'MUL':
            
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) * int(value2)))
        elif opcode == 'SUB':
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) - int(value2)))
        elif opcode == 'IDIV':
            if value2 == '0':
                ErrorHandler.errorExit(57, "Division by zero")
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) // int(value2)))

    # Function for relation instructions
    def relationOP(self, opcode, counter):
        value1, type1 = self.frames.getValueAndType(self.instList[counter][1].arg2)
        value2, type2 = self.frames.getValueAndType(self.instList[counter][1].arg3)

        if value1 is None:
            value1 = ''
        if value2 is None:
            value2 = ''
        if not(type1 == type2) and not(opcode == 'EQ' and (type1 == 'nil' or type2 =='nil')):
            ErrorHandler.errorExit(53, "Bad operand types")
        if opcode == 'LT':
            if type1 == 'int':
                if int(value1) < int(value2):
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            elif type1 == 'string' or type1 == 'bool':
                if value1 < value2:
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            else: ErrorHandler.errorExit(53, "Bad operand types")
        elif opcode == 'GT':
            if type1 == 'int':
                if int(value1) > int(value2):
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            elif type1 == 'string' or type1 == 'bool':
                if value1 > value2:
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            else: ErrorHandler.errorExit(53, "Bad operand types")
        elif opcode == 'EQ':
            if value1 == value2:
                self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
            else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
        elif opcode == 'AND':
            if type1 == 'bool':
                if value1 == 'true' and value2 == 'true':
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            else: ErrorHandler.errorExit(53, "Bad operand types")
        elif opcode == 'OR':
            if type1 == 'bool':
                if value1 == 'true' or value2 == 'true':
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            else: ErrorHandler.errorExit(53, "Bad operand types")

    # Jump to label
    def jump(self, counter):
        value, type = self.frames.getValueAndType(self.instList[counter][1].arg1)
        if value not in self.labels:
            ErrorHandler.errorExit(52, "Semantic Error")
        number = int(self.labels[value])
        for x in range(len(self.instList)):
            if self.instList[x][0] == number:
                counter = x
                break
        return counter
    
    # Function for jump conditions
    def jumpConditions(self, opcode, counter):
        prev = counter
        value, type = self.frames.getValueAndType(self.instList[counter][1].arg1)
        if value not in self.labels:
            ErrorHandler.errorExit(52, "Semantic Error")
        value1, type1 = self.frames.getValueAndType(self.instList[counter][1].arg2)
        value2, type2 = self.frames.getValueAndType(self.instList[counter][1].arg3)
        if not(type1 == type2) and not(type1 == 'nil' or type2 == 'nil'):
            ErrorHandler.errorExit(53, "Bad operand types")
        if type1 == 'int':
            value1 = int(value1)
        if type2 == 'int':
            value2 = int(value2)
        if (value1 != value2 and opcode == 'JUMPIFNEQ') or (value1 == value2 and opcode == 'JUMPIFEQ'):
            counter = self.jump(counter)
            return counter
        else: return prev

    # Interpret every instruction in sorted order
    def run(self, inputFile):
        if inputFile != sys.stdin:
            try:
                f = open(inputFile, "r")
            except OSError:
                ErrorHandler.errorExit(11, "Couldn't open file")
        instruction = 0
        while instruction < len(self.instList):
            if self.instList[instruction][1].opcode == 'BREAK': 
                print("Instruction order: " + str(self.instList[instruction][0]), file=sys.stderr)
                print("Global frame: " + self.frames.globalFrame, file=sys.stderr)
                print("Tmp frame: " + self.tmpFrame, file=sys.stderr)
                print("Frame stack: " + self.frames.frameStack, file=sys.stderr)            
            elif self.instList[instruction][1].opcode == 'DEFVAR':
                frame, name = self.instList[instruction][1].arg1['value'].split('@', 1)
                frameInsert = self.frames.getFrame(frame)
                if frameInsert != 'UNDEFINED':
                    if name not in frameInsert:
                        frameInsert[name] = {'type': None, 'value': None}
                    else:
                        ErrorHandler.errorExit(52, "Semantic Error")
                else: ErrorHandler.errorExit(55, "Invalid frame")
            elif self.instList[instruction][1].opcode == 'MOVE':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                if value == 'nil':
                    value = ''
                self.frames.setvar(self.instList[instruction][1].arg1, type, value)
            elif self.instList[instruction][1].opcode == 'WRITE':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg1)
                if value is None or (value == 'nil' and type != 'string'):
                    value = ''
                print(value, end='')
            elif self.instList[instruction][1].opcode == 'DPRINT':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg1)
                if value is None or (value == 'nil' and type != 'string'):
                    value = ''
                print(value, file=sys.stderr, end='')   
            elif self.instList[instruction][1].opcode == 'EXIT':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg1)
                if type != 'int':
                    ErrorHandler.errorExit(53, "Bad operand types")
                if value.isnumeric():
                    if int(value) >= 0 and int(value) <= 47:
                        sys.exit(int(value))
                    else: ErrorHandler.errorExit(57, "Wrong operand value")
                else: ErrorHandler.errorExit(57, "Wrong operand value")
            elif self.instList[instruction][1].opcode == 'CREATEFRAME':
                self.frames.createTmpFrame()
            elif self.instList[instruction][1].opcode == 'PUSHFRAME':
                if self.frames.tmpFrame is not None:
                    self.frames.frameStack.append(self.frames.tmpFrame)
                else: ErrorHandler.errorExit(55, "Invalid frame")
                self.frames.tmpFrame = None
            elif self.instList[instruction][1].opcode == 'POPFRAME':
                if self.frames.frameStack:
                    self.frames.tmpFrame = self.frames.frameStack.pop()
                else: ErrorHandler.errorExit(55, "Invalid frame")
            elif self.instList[instruction][1].opcode == 'TYPE':
                self.frames.type = True
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                if value is None:
                    value = ''
                    type = ''
                if type == 'nil':
                    value = ''
                self.frames.setvar(self.instList[instruction][1].arg1, 'string', type)
            elif re.match('^(ADD|SUB|MUL|IDIV)$',self.instList[instruction][1].opcode):
                self.arithmetic(self.instList[instruction][1].opcode, instruction)
            elif re.match('^(LT|GT|EQ|AND|OR)$',self.instList[instruction][1].opcode):
                self.relationOP(self.instList[instruction][1].opcode, instruction)
            elif self.instList[instruction][1].opcode == 'NOT':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                if type == 'bool':
                    if value == 'true':
                        self.frames.setvar(self.instList[instruction][1].arg1, 'bool', 'false')
                    else: self.frames.setvar(self.instList[instruction][1].arg1, 'bool', 'true')
                else: ErrorHandler.errorExit(53, "Bad operand types")
            elif self.instList[instruction][1].opcode == 'CONCAT':
                value1, type1 = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                value2, type2 = self.frames.getValueAndType(self.instList[instruction][1].arg3)
                if not(type1 == type2 and type1 == 'string'):
                    ErrorHandler.errorExit(53, "Bad operand types")
                if value1 is None:
                    value1 = ''
                if value2 is None:
                    value2 = ''
                self.frames.setvar(self.instList[instruction][1].arg1, 'string', value1 + value2)
            elif self.instList[instruction][1].opcode == 'STRLEN':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                if value is None:
                    value = ''
                if type != 'string':
                    ErrorHandler.errorExit(53, "Bad operand types")
                self.frames.setvar(self.instList[instruction][1].arg1, 'int', len(value))
            elif self.instList[instruction][1].opcode == 'GETCHAR':
                value1, type1 = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                value2, type2 = self.frames.getValueAndType(self.instList[instruction][1].arg3)
                if type1 != 'string' or type2 != 'int':
                    ErrorHandler.errorExit(53, "Bad operand types")
                if int(value2) > len(value1) - 1 or int(value2) < 0:
                    ErrorHandler.errorExit(58, "Invalid string usage")
                self.frames.setvar(self.instList[instruction][1].arg1, 'string', value1[int(value2)])
            elif self.instList[instruction][1].opcode == 'SETCHAR':
                value1, type1 = self.frames.getValueAndType(self.instList[instruction][1].arg1)
                value2, type2 = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                value3, type3 = self.frames.getValueAndType(self.instList[instruction][1].arg3)
                if type1 != 'string' or type3 != 'string' or type2 != 'int':
                    ErrorHandler.errorExit(53, "Bad operand types")
                if int(value2) > len(value1) - 1 or int(value2) < 0 or value3 is None:
                    ErrorHandler.errorExit(58, "Invalid string usage")
                if len(value3) > 1:
                    value3 = value3[0]
                value1 = value1[:int(value2)] + value3 + value[int(value2)+1:]
                self.frames.setvar(self.instList[instruction][1].arg1, 'string', value1)
            elif self.instList[instruction][1].opcode == 'STRI2INT':
                value1, type1 = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                value2, type2 = self.frames.getValueAndType(self.instList[instruction][1].arg3)
                if type1 != 'string' or type2 != 'int':
                    ErrorHandler.errorExit(53, "Bad operand types")
                if int(value2) > len(value1) - 1 or int(value2) < 0:
                    ErrorHandler.errorExit(58, "Invalid string usage")
                self.frames.setvar(self.instList[instruction][1].arg1, 'int', ord(value1[int(value2)]))
            elif self.instList[instruction][1].opcode == 'INT2CHAR':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                if type != 'int':
                    ErrorHandler.errorExit(53, "Bad operand types")
                try:
                    value = chr(int(value))
                except ValueError:
                    ErrorHandler.errorExit(58, "Invalid string usage")
                self.frames.setvar(self.instList[instruction][1].arg1, 'string', value)
            elif self.instList[instruction][1].opcode == 'PUSHS':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg1)
                self.stackItems += 1
                self.dataStack.append((type, value))
            elif self.instList[instruction][1].opcode == 'POPS':
                if self.stackItems > 0:
                    type, value = self.dataStack.pop()
                    self.frames.setvar(self.instList[instruction][1].arg1, type, value)
                    self.stackItems -= 1
                else: ErrorHandler.errorExit(56, "Missing value")
            elif self.instList[instruction][1].opcode == 'JUMP':
                instruction = self.jump(instruction)
            elif self.instList[instruction][1].opcode == 'CALL':
                self.callStack.append(instruction + 1)
                instruction = self.jump(instruction)
            elif self.instList[instruction][1].opcode == 'RETURN':
                if len(self.callStack) > 0:
                    instruction = self.callStack.pop()
                    continue
                else: ErrorHandler.errorExit(56, "Missing value")
            elif self.instList[instruction][1].opcode == 'JUMPIFEQ' or self.instList[instruction][1].opcode == 'JUMPIFNEQ':
                instruction = self.jumpConditions(self.instList[instruction][1].opcode, instruction)
            elif self.instList[instruction][1].opcode == 'READ':
                value, type = self.frames.getValueAndType(self.instList[instruction][1].arg2)
                if inputFile == sys.stdin:
                    try:
                        foo = input()
                    except EOFError:
                        foo = ''
                else: foo = f.readline()

                if len(foo) == 0:
                    value = 'nil'
                    foo = 'nil'
                elif value == 'bool':
                    foo = foo.rstrip('\n')
                    if foo.lower() == 'true':
                        foo = 'true'
                    else: foo = 'false'
                elif value == 'int':
                    try:
                        foo = int(foo)
                    except ValueError:
                        value = 'nil'
                        foo = 'nil'
                elif value == 'string':
                    if len(foo) != 0 and foo[-1] == '\n':
                        foo = foo[:-1]
                self.frames.setvar(self.instList[instruction][1].arg1, value, foo)
          
            instruction += 1
            