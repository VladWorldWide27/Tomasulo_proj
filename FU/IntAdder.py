from units.functional_unit import FunctionalUnit


class IntegerAdder(FunctionalUnit):
    def __init__(self, count, ex_cycles):
        FunctionalUnit.__init__(self, 'integer adder', count, ex_cycles, False)