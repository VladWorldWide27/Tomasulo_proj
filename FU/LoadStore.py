from FU.FU import FunctionalUnit


class AddressAdder(FunctionalUnit):
    def __init__(self, count, ex_cycles):
        #name, count, ex_cycles, pipelined
        FunctionalUnit.__init__(self, 'address adder', count, ex_cycles, False)