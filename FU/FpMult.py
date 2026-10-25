from units.functional_unit import FunctionalUnit


class FPMultiplier(FunctionalUnit):
    def __init__(self, count, ex_cycles):
        FunctionalUnit.__init__(self, 'fp multiplier', count, ex_cycles, True)