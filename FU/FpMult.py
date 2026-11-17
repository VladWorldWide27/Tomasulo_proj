from FU.FU import FunctionalUnit

#Handles Mult and MUlt.d.
class FPMultiplier(FunctionalUnit):
    def __init__(self, count, ex_cycles):
        #name, count, ex_cycles, pipelined
        FunctionalUnit.__init__(self, 'fp multiplier', count, ex_cycles, True)