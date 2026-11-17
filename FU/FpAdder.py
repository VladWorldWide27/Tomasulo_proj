from FU.FU import FunctionalUnit
#Handles Add.d and Sub.d.

class FPAdder(FunctionalUnit):
    def __init__(self, count, ex_cycles):
        #name, count, ex_cycles, pipelined
        FunctionalUnit.__init__(self, 'fp adder', count, ex_cycles, True)