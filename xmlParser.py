import xml.etree.ElementTree as ET
import re
import sys
from core import Interpret

# Class that stores whole instruction
class Instruction:
    def __init__(self, opcode, arg1=None, arg2=None, arg3=None):
        self.opcode = opcode
        if arg1 is not None:
            self.arg1 = {'type': arg1.attrib['type'], 'value': arg1.text}
        if arg2 is not None:
            self.arg2 = {'type': arg2.attrib['type'], 'value': arg2.text}
        if arg3 is not None:
            self.arg3 = {'type': arg3.attrib['type'], 'value': arg3.text}


class XMLParser:
    def __init__(self, xmlFile):
        self.instructions = {
        'MOVE': ['var', 'symb'],
        'CREATEFRAME': [],
        'PUSHFRAME': [],
        'POPFRAME': [],
        'DEFVAR': ['var'],
        'CALL': ['label'],
        'RETURN': [],
        'PUSHS': ['symb'],
        'POPS': ['var'],
        'ADD': ['var', 'symb', 'symb'],
        'SUB': ['var', 'symb', 'symb'],
        'MUL': ['var', 'symb', 'symb'],
        'IDIV': ['var', 'symb', 'symb'],
        'LT': ['var', 'symb', 'symb'],
        'GT': ['var', 'symb', 'symb'],
        'EQ': ['var', 'symb', 'symb'],
        'AND': ['var', 'symb', 'symb'],
        'OR': ['var', 'symb', 'symb'],
        'NOT': ['var', 'symb'],
        'INT2CHAR': ['var', 'symb'],
        'STRI2INT': ['var', 'symb', 'symb'],
        'READ': ['var', 'type'],
        'WRITE': ['symb'],
        'CONCAT': ['var', 'symb', 'symb'],
        'STRLEN': ['var', 'symb'],
        'GETCHAR': ['var', 'symb', 'symb'],
        'SETCHAR': ['var', 'symb', 'symb'],
        'TYPE': ['var', 'symb'],
        'LABEL': ['label'],
        'JUMP': ['label'],
        'JUMPIFEQ': ['label', 'symb', 'symb'],
        'JUMPIFNEQ': ['label', 'symb', 'symb'],
        'EXIT': ['symb'],
        'DPRINT': ['symb'],
        'BREAK': []
        }
        try:
            xml = ET.parse(xmlFile)
            self.root = xml.getroot()
        except FileNotFoundError:
            sys.exit(31)
        except ET.ParseError:
            sys.exit(31)

    # Check whole XML and insert instruction in order into sorted list
    def checkXML(self):
        if self.root.tag != 'program':
            sys.exit(32)
        for atr in self.root.attrib:
            if atr not in ['language', 'name', 'description']:
                sys.exit(32)
        if 'language' not in self.root.attrib:
            sys.exit(32)
        if not re.match('^ippcode21$', self.root.attrib['language'], re.IGNORECASE):
            sys.exit(32)
        order = []
        instList = {}
        labels = {}
        for inst in self.root:
            if inst.tag != 'instruction':
                sys.exit(32)  
            if not('opcode' in inst.attrib and 'order' in inst.attrib):
                sys.exit(32)
            if inst.attrib['order'].isnumeric():
                if int(inst.attrib['order']) <= 0:
                    sys.exit(32)
            else: sys.exit(32)
            order.append(inst.attrib['order'])
            inst.attrib['opcode'] = inst.attrib['opcode'].upper()
            if inst.attrib['opcode'] not in self.instructions:
                sys.exit(32)
            args = len(self.instructions[inst.attrib['opcode']])
            
            counter = 1
            for arg in inst:
                if counter > args:
                    sys.exit(32)
                string = arg.tag + str(arg.attrib)
                number = int(arg.tag.split("arg")[1])
                if not re.match('^arg[1-3]{1}{\'type\':\s\'(var|int|bool|string|label|type|nil)\'}', string):
                    sys.exit(32)
                if args == 0:
                    if arg:
                        sys.exit(32)
                elif args == 1:
                    self.checkArg(self.instructions[inst.attrib['opcode']][number-1], arg)
                elif args == 2:
                    self.checkArg(self.instructions[inst.attrib['opcode']][number-1], arg)
                elif args == 3:
                    self.checkArg(self.instructions[inst.attrib['opcode']][number-1], arg)
                counter += 1

            args = len(self.instructions[inst.attrib['opcode']])
            if args == 0:
                instruction = Instruction(inst.attrib['opcode'])
                instList[int(inst.attrib['order'])] = instruction
            elif args == 1:
                instruction = Instruction(inst.attrib['opcode'], arg1=inst[0])
                instList[int(inst.attrib['order'])] = instruction
                if inst.attrib['opcode'] == 'LABEL':
                    label = inst[0].text
                    if label in labels:
                        sys.exit(52)
                    labels[label] = inst.attrib['order']
            elif args == 2:
                instruction = Instruction(inst.attrib['opcode'], arg1=inst[0], arg2=inst[1])
                instList[int(inst.attrib['order'])] = instruction
            elif args == 3:
                instruction = Instruction(inst.attrib['opcode'], arg1=inst[0], arg2=inst[1], arg3=inst[2])
                instList[int(inst.attrib['order'])] = instruction
        if len(order) != len(set(order)):
            sys.exit(32)
        instList = sorted(instList.items(), key=lambda x: x[0])
        return instList, labels     

    # Check if values of arguments are correct
    def checkArg(self, argType, arg):
        if argType == 'type':
            if not re.match('^(int|bool|string)$', arg.text):
                sys.exit(32)
        elif argType == 'var':
            if not re.match('^(LF|TF|GF)@[a-zA-Z_\-$&%!?*][a-zA-Z0-9_\-$&%!?*]*$', arg.text):
                sys.exit(32)
        elif argType == 'label':
            if not re.match('^[a-zA-Z_\-$&%!?*][a-zA-Z0-9_\-$&%!?*]*$', arg.text):
                sys.exit(32)
        elif argType == 'symb':
            if arg.attrib['type'] == 'int':
                if not re.match('^[+-]?[0-9]+$', arg.text):
                    sys.exit(32)
            elif arg.attrib['type'] == 'bool':
                if not re.match('^(true|false)$', arg.text):
                    sys.exit(32)
            elif arg.attrib['type'] == 'nil':
                if not re.match('^nil$', arg.text):
                    sys.exit(32)
            elif arg.attrib['type'] == 'var':
                self.checkArg('var', arg)
            elif arg.attrib['type'] == 'string':
                if arg.text != None:
                    if not re.match('^(([^\\\\])|(\\\\(?=\d{3})))*$', arg.text):
                        sys.exit(32)
                    try:
                        arg.text = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), arg.text)
                    except ValueError:
                        sys.exit(32)
        else: sys.exit(32)
        