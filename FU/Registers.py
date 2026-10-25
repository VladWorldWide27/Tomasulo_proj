from Isa import NUM_REGS


class RegisterFiles:
    def __init__(self, iregs, fregs):
        self.ireg = {('i', n): 0 for n in range(NUM_REGS)}
        self.freg = {('f', n): 0.0 for n in range(NUM_REGS)}
        self.ireg.update(iregs)
        self.freg.update(fregs)
        self.ireg[('i', 0)] = 0

    def read(self, reg):
        return self.ireg[reg] if reg[0] == 'i' else self.freg[reg]

    def write(self, reg, value):
        if reg[0] == 'f':
            self.freg[reg] = value
        elif reg[1] != 0:
            self.ireg[reg] = value

    def nonzero_int(self):
        return sorted(n for n in range(NUM_REGS) if self.ireg[('i', n)] != 0)

    def nonzero_fp(self):
        return sorted(n for n in range(NUM_REGS) if self.freg[('f', n)] != 0)