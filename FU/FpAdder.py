from FU.FU import FunctionalUnit


class FPAdder(FunctionalUnit):
    def __init__(self, count, ex_cycles):
        FunctionalUnit.__init__(self, 'fp adder', count, ex_cycles, True)