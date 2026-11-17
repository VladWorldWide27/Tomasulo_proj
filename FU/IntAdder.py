from FU.FU import FunctionalUnit

# Handles Add, Addi, Sub, Bne, Beq, Mult, 
class IntegerAdder(FunctionalUnit):
    def __init__(self, count, ex_cycles):
        #name, count, ex_cycles, pipelined
        FunctionalUnit.__init__(self, 'integer adder', count, ex_cycles, False)