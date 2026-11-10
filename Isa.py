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
        self.idx = idx
        self.op = op
        self.cls = OP_CLASS[op]
        self.text = text
        self.dest = None
        self.srcs = []
        self.imm = 0
        self.base = None
        self.target = None
        self.issue = None
        self.ex_start = None
        self.ex_end = None
        self.mem_start = None
        self.mem_end = None
        self.wb = None
        self.commit = None
        self.rob_id = None
        self.tags = []
        self.vals = []
        self.ready_cycle = []
        self.address = None
        self.result = None
        self.predicted_next = None
        self.fault = None
        self.rs_released = False
        self.seq = None

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


def parse_reg(tok):
    tok = tok.strip().rstrip(',')
    m = re.fullmatch(r'([RrFf])(\d+)', tok)
    if not m:
        raise ParseError('bad register: %s' % tok)
    kind = 'i' if m.group(1).lower() == 'r' else 'f'
    num = int(m.group(2))
    if num >= NUM_REGS:
        raise ParseError('register out of range: %s' % tok)
    return (kind, num)


def reg_name(reg):
    return ('R' if reg[0] == 'i' else 'F') + str(reg[1])