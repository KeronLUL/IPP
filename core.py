from frames import Frames
import sys
import re

class Interpret:
    def __init__(self, list):
        self.frames = Frames()
        self.instList = list
        self.dataStack = []
        self.stackItems = 0
        self.labels = {}

    def arithmetic(self, opcode, counter):
        value1, type1 = self.frames.getValueAndType(self.instList[counter][1].arg2)
        value2, type2 = self.frames.getValueAndType(self.instList[counter][1].arg3)

        if not(type1 == type2 and type1 == 'int'):
            exit(53)
        if opcode == 'ADD':
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) + int((value2))))
        elif opcode == 'MUL':
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) * int(value2)))
        elif opcode == 'SUB':
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) - int(value2)))
        elif opcode == 'IDIV':
            if value2 == '0':
                exit(57)
            self.frames.setvar(self.instList[counter][1].arg1, 'int', (int(value1) // int(value2)))

    def relationOP(self, opcode, counter):
        value1, type1 = self.frames.getValueAndType(self.instList[counter][1].arg2)
        value2, type2 = self.frames.getValueAndType(self.instList[counter][1].arg3)

        
        if not(type1 == type2):
            exit(53)
        if opcode == 'LT':
            if type1 == 'int' or type1 == 'string':
                if int(value1) < int(value2):
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')

        elif opcode == 'GT':
            if type1 == 'int' or type1 == 'string':
                if int(value1) > int(value2):
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
        elif opcode == 'EQ':
            if type1 == 'int' or type1 == 'string':
                if int(value1) == int(value2):
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
        elif opcode == 'AND':
            if type1 == 'bool':
                if value1 == value2 and value1 == 'true':
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            else: exit(53)
        elif opcode == 'OR':
            if type1 == 'bool':
                if value1 == 'true' or value2 == 'true':
                    self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'true')
                else: self.frames.setvar(self.instList[counter][1].arg1, 'bool', 'false')
            else: exit(53)


    def run(self):
        for x in range(len(self.instList)):
            if self.instList[x][1].opcode == 'DEFVAR':
                self.frames.defvar(self.instList[x][1].arg1)
            elif self.instList[x][1].opcode == 'MOVE':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg2)
                if value == 'nil':
                    value = ''
                self.frames.setvar(self.instList[x][1].arg1, type, value)

            elif self.instList[x][1].opcode == 'WRITE':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg1)
                if value is not None:
                    if value == 'nil' and type != 'string':
                        value = ''
                    print(value, end='')
                else: exit(56)
            elif self.instList[x][1].opcode == 'DPRINT':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg1)
                if value is not None:
                    if value == 'nil':
                        value = ''
                    print(value, file=sys.stderr, end='')
                else: exit(56)
            elif self.instList[x][1].opcode == 'EXIT':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg1)
                if type != 'int':
                    exit(53)
                if value.isnumeric():
                    if int(value) >= 0 and int(value) <= 47:
                        exit(int(value))
                    else: exit(57)
                else: exit(57)
            elif self.instList[x][1].opcode == 'CREATEFRAME':
                self.frames.createTmpFrame()
            elif self.instList[x][1].opcode == 'PUSHFRAME':
                if self.frames.tmpFrame is not None:
                    self.frames.frameStack.append(self.frames.tmpFrame)
                else: exit(55)
                self.frames.tmpFrame = None
            elif self.instList[x][1].opcode == 'POPFRAME':
                if self.frames.frameStack:
                    self.frames.tmpFrame = self.frames.frameStack.pop()
                else: exit(55)
                
            elif self.instList[x][1].opcode == 'TYPE':
                
                value, type = self.frames.getValueAndType(self.instList[x][1].arg2)
                if type == 'nil':
                    value = ''

                self.frames.setvar(self.instList[x][1].arg1, 'string', type)
            elif re.match('^(ADD|SUB|MUL|IDIV)$',self.instList[x][1].opcode):
                self.arithmetic(self.instList[x][1].opcode, x)
            elif re.match('^(LT|GT|EQ|AND|OR)$',self.instList[x][1].opcode):
                self.relationOP(self.instList[x][1].opcode, x)
            elif self.instList[x][1].opcode == 'NOT':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg2)
                if type == 'bool':
                    if value == 'true':
                        self.frames.setvar(self.instList[x][1].arg1, 'bool', 'false')
                    else: self.frames.setvar(self.instList[x][1].arg1, 'bool', 'true')
                else: exit(53)
            elif self.instList[x][1].opcode == 'CONCAT':
                value1, type1 = self.frames.getValueAndType(self.instList[x][1].arg2)
                value2, type2 = self.frames.getValueAndType(self.instList[x][1].arg3)
                if not(type1 == type2 and type1 == 'string'):
                    exit(53)
                if value1 is None:
                    value1 = ''
                if value2 is None:
                    value2 = ''
                self.frames.setvar(self.instList[x][1].arg1, 'string', value1 + value2)
            elif self.instList[x][1].opcode == 'STRLEN':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg2)
                if value is None:
                    value = ''
                if type != 'string':
                    exit(53)
                self.frames.setvar(self.instList[x][1].arg1, 'int', len(value))
            elif self.instList[x][1].opcode == 'GETCHAR':
                value1, type1 = self.frames.getValueAndType(self.instList[x][1].arg2)
                value2, type2 = self.frames.getValueAndType(self.instList[x][1].arg3)
                if type1 != 'string' or type2 != 'int':
                    exit(53)
                if int(value2) > len(value1) - 1 or int(value2) < 0:
                    exit(58)
                self.frames.setvar(self.instList[x][1].arg1, 'string', value1[int(value2)])
            elif self.instList[x][1].opcode == 'SETCHAR':
                value1, type1 = self.frames.getValueAndType(self.instList[x][1].arg1)
                value2, type2 = self.frames.getValueAndType(self.instList[x][1].arg2)
                value3, type3 = self.frames.getValueAndType(self.instList[x][1].arg3)
                if type1 != 'string' or type3 != 'string' or type2 != 'int':
                    exit(53)
                if int(value2) > len(value1) - 1 or int(value2) < 0 or value3 is None:
                    exit(58)
                if len(value3) > 1:
                    value3 = value3[0]
                value1 = value1[:int(value2)] + value3 + value[int(value2)+1:]
                self.frames.setvar(self.instList[x][1].arg1, 'string', value1)
            elif self.instList[x][1].opcode == 'STRI2INT':
                value1, type1 = self.frames.getValueAndType(self.instList[x][1].arg2)
                value2, type2 = self.frames.getValueAndType(self.instList[x][1].arg3)
                if type1 != 'string' or type2 != 'int':
                    exit(53)
                if int(value2) > len(value1) - 1 or int(value2) < 0:
                    exit(58)
                self.frames.setvar(self.instList[x][1].arg1, 'int', ord(value1[int(value2)]))
            elif self.instList[x][1].opcode == 'INT2CHAR':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg2)
                if type != 'int':
                    exit(53)
                try:
                    value = chr(int(value))
                except ValueError:
                    exit(58)
                self.frames.setvar(self.instList[x][1].arg1, 'string', value)
            elif self.instList[x][1].opcode == 'PUSHS':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg1)
                self.stackItems += 1
                self.dataStack.append((type, value))
            elif self.instList[x][1].opcode == 'POPS':
                if self.stackItems > 0:
                    type, value = self.dataStack.pop()
                    self.frames.setvar(self.instList[x][1].arg1, type, value)
                    self.stackItems -= 1
                else: exit(56)
            elif self.instList[x][1].opcode == 'BREAK':
                print("Instruction order: " + str(self.instList[x][0]), file=sys.stderr)
            elif self.instList[x][1].opcode == 'LABEL':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg1)
                if value in self.labels:
                    exit(52)
                self.labels[value] = self.instList[x][0]
            elif self.instList[x][1].opcode == 'CALL':
                value, type = self.frames.getValueAndType(self.instList[x][1].arg1)
                if value not in self.labels:
                    exit(52)
                
                