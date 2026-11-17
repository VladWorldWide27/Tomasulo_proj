from Isa import NUM_REGS


class RegisterFiles:
    def __init__(self, iregs, fregs):
        self.ireg = {('i', n): 0 for n in range(NUM_REGS)}  #int
        self.freg = {('f', n): 0.0 for n in range(NUM_REGS)} # float
        self.ireg.update(iregs)
        self.freg.update(fregs)
        self.ireg[('i', 0)] = 0

    #read if the val is an int or a float register
    #called from issue
    def read(self, reg):
        return self.ireg[reg] if reg[0] == 'i' else self.freg[reg]

    #almost identical process of choosing int or float. Called from Commit. ARF is used by commit and not CDB
    def write(self, reg, value):
        if reg[0] == 'f':
            self.freg[reg] = value
        elif reg[1] != 0:
            self.ireg[reg] = value

     #for final output, return register numbers 
    def nonzero_int(self):
        return sorted(n for n in range(NUM_REGS) if self.ireg[('i', n)] != 0)

    def nonzero_fp(self):
        return sorted(n for n in range(NUM_REGS) if self.freg[('f', n)] != 0)