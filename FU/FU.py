class FunctionalUnit:
    def __init__(self, name, count, ex_cycles, pipelined):
        self.name = name
        self.count = count
        self.ex_cycles = ex_cycles
        self.pipelined = pipelined
        self.free_at = [0] * count
        self.starts = {}

    def can_accept(self, cycle):
        if self.pipelined:
            return self.starts.get(cycle, 0) < self.count
        return any(free < cycle for free in self.free_at)

    def accept(self, cycle):
        if self.pipelined:
            self.starts[cycle] = self.starts.get(cycle, 0) + 1
        else:
            for i, free in enumerate(self.free_at):
                if free < cycle:
                    self.free_at[i] = cycle + self.ex_cycles - 1
                    break
        return cycle + self.ex_cycles - 1