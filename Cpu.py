from Isa import INT, FPA, FPM, LSU
from Core.cdb import CommonDataBus
from Core.RAT import RegisterAliasTable
from Core.Reservation import ReservationStations
from Core.Rob import ReorderBuffer
from FU.FpAdder import FPAdder
from FU.FpMult import FPMultiplier
from FU.IntAdder import IntegerAdder
from FU.LoadStore import AddressAdder
from FU.Memory import DataMemory
from FU.Registers import RegisterFiles
from Ops import commit, execute, issue, mem_access, write_back


class CPU:
    def __init__(self, cfg, prog, iregs, fregs, mem):
        self.cfg = cfg
        self.prog = prog
        self.registers = RegisterFiles(iregs, fregs)
        self.memory = DataMemory(mem, cfg.mem_cycles)
        self.units = {
            INT: IntegerAdder(cfg.fu[INT], cfg.ex[INT]),
            FPA: FPAdder(cfg.fu[FPA], cfg.ex[FPA]),
            FPM: FPMultiplier(cfg.fu[FPM], cfg.ex[FPM]),
            LSU: AddressAdder(cfg.fu[LSU], cfg.ex[LSU]),
        }
        self.stations = ReservationStations(cfg.rs)
        self.rob = ReorderBuffer(cfg.rob)
        self.rat = RegisterAliasTable()
        self.cdb = CommonDataBus(cfg.cdb_buffer)
        self.next_issue = 0
        self.cycle = 0
        self.stalls = {}

    def step(self):
        self.cycle += 1
        commit.run(self)
        write_back.run(self)
        mem_access.run(self)
        issue.run(self)
        execute.run(self)

    def finished(self):
        return self.next_issue >= len(self.prog) and all(i.commit for i in self.prog)

    def run(self, on_cycle=None, limit=100000):
        while self.cycle < limit:
            self.step()
            if on_cycle is not None:
                on_cycle(self)
            if self.finished():
                break
        return self.cycle