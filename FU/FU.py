class FunctionalUnit:
     #resource tracker for a functional unit
     #called by execute and write back to determine if a unit can accept an instruction and when it will be done
    def __init__(self, name, count, ex_cycles, pipelined):
        self.name = name
        self.count = count
        self.ex_cycles = ex_cycles
        self.pipelined = pipelined
        self.free_at = [0] * count
        self.starts = {}
        self.frozen_at = None #comes from write_back

    #asks if the unit can accept a new instruction at the given cycle
    def can_accept(self, cycle):
        #check if the unit sits the cycle out
        if self.frozen_at == cycle:
            return False
        #check if the unit is pipelined or not
        if self.pipelined:
            return self.starts.get(cycle, 0) < self.count
        #check if the unit finished working
        return any(free < cycle for free in self.free_at)

    #units get claimed
    def accept(self, cycle):
        if self.pipelined:
            self.starts[cycle] = self.starts.get(cycle, 0) + 1
        else:
            #find teh first free unit and claim it
            for i, free in enumerate(self.free_at):
                if free < cycle:
                    self.free_at[i] = cycle + self.ex_cycles - 1
                    break
        return cycle + self.ex_cycles - 1
    #CBD is done, but there is no place to put the result, so the unit is held up for a cycle
    def hold(self, ins):
        i = self.free_at.index(ins.ex_end)
        ins.ex_end += 1
        self.free_at[i] = ins.ex_end