import re


INT = 'int_adder'
FPA = 'fp_adder'
FPM = 'fp_mult'
LSU = 'ld_st'
NOPU = 'nop'
BRANCHES = ('beq', 'bne')

OP_CLASS = {
    'add': INT, 'addi': INT, 'sub': INT,
    'add.d': FPA, 'sub.d': FPA,
    'mult': FPM,
    'mult.d': FPM,
    'ld': LSU, 'sd': LSU,
    'nop': NOPU,
    'beq': INT, 'bne': INT,
}

MEM_WORDS = 64
MEM_BYTES = 256
NUM_REGS = 32


class Instruction:
    def __init__(self, idx, op, text):
        self.idx = idx #index in the program from first line
        self.op = op #opcode
        self.cls = OP_CLASS[op] # what unit runs the op
        self.text = text #original text of the instruction
        self.dest = None # destination register
        self.srcs = [] #source registers
        self.imm = 0 #immediate or offset
        self.base = None #base register for load/store
        self.target = None #target address for branches
        self.issue = None #cycle when instruction is issued
        self.ex_start = None #cycle when instruction starts execution
        self.ex_end = None # cycle when instruction finishes execution
        self.mem_start = None #cycle when instruction starts memory access
        self.mem_end = None #cycle when instruction finishes memory access
        self.wb = None #cycle when instruction writes back
        self.commit = None #cycle when instruction is committed
        self.rob_id = None #reorder buffer entry ID
        self.tags = [] #tags of the reservation stations that hold this instruction
        self.vals = [] #values of the source operands 
        self.ready_cycle = [] #cycle when the source operands are ready
        self.address = None #memory address for load/store
        self.result = None #result of the instruction
        self.predicted_next = None #predicted next instruction index for branches
        self.fault = None #fault type for load/store
        self.flushed = None #cycle when instruction is flushed due to misprediction
        self.forwarded = False #whether the instruction's result was forwarded to another instruction
        self.rs_released = False #whether the instruction's reservation station was released
        self.seq = None #sequence number for the instruction, used for ordering in the ROB

    #copy the instruction for each line it gets issued
    def fresh_copy(self, seq):
        ins = Instruction(self.idx, self.op, self.text)
        ins.dest = self.dest
        ins.srcs = list(self.srcs)
        ins.imm = self.imm
        ins.base = self.base
        ins.target = self.target
        ins.seq = seq
        return ins



class ParseError(Exception):
    pass


#convert a register format into text
def parse_reg(tok):
    tok = tok.strip().rstrip(',')
    m = re.fullmatch(r'([RrFf])(\d+)', tok)
    if not m:
        raise ParseError('horrible register: %s' % tok)
    kind = 'i' if m.group(1).lower() == 'r' else 'f'
    num = int(m.group(2))
    if num >= NUM_REGS:
        raise ParseError('register out of bounds :( : %s' % tok)
    return (kind, num)

#only for report
def reg_name(reg):
    return ('R' if reg[0] == 'i' else 'F') + str(reg[1])