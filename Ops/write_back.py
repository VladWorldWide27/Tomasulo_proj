from Isa import NOPU, BRANCHES, INT , FPA, FPM
from Core.cdb import MEMORY, cdb_unit, finish_cycle


def completed(ins, cycle):
    if ins.op == 'ld' or ins.cls == NOPU:
        return ins.mem_end is not None and ins.mem_end < cycle
    return ins.ex_end is not None and ins.ex_end < cycle


def run(cpu):
    for ins in cpu.issued:
        if ins.op in BRANCHES and ins.ex_end is not None and ins.ex_end < cpu.cycle:
            cpu.stations.release(ins)
    requesters = [ins for ins in cpu.issued
                  if ins.wb is None and ins.op != 'sd' and ins.op not in BRANCHES
                  and completed(ins, cpu.cycle)]
    winner = cpu.cdb.arbitrate(requesters)
    if winner is not None:
        cpu.cdb.grant(winner, cpu.cycle)
        entry = cpu.rob.entry(winner.rob_id)
        entry.value = winner.result
        entry.ready = True
        if winner.op != 'ld':
            cpu.stations.release(winner)
        cpu.cdb.broadcast(cpu.issued, winner.rob_id, winner.result, cpu.cycle)
    check_buffers(cpu, [i for i in requesters if i is not winner])


def check_buffers(cpu, losers):
    cpu.cdb_room = {}
    for unit in (INT, FPA, FPM, MEMORY):
        copies = 1 if unit == MEMORY else cpu.cfg.fu[unit]
        capacity = copies * (cpu.cdb.buffer_entries + 1)
        waiting = [i for i in losers if cdb_unit(i) == unit]
        finishing = [i for i in cpu.issued
                     if cdb_unit(i) == unit and finish_cycle(i) == cpu.cycle]
        extra = len(waiting) + len(finishing) - capacity
        cpu.cdb_room[unit] = max(0, -extra)
        if extra <= 0:
            continue
        cpu.cdb_stalls.add((cpu.cycle, unit))
        if unit == MEMORY:
            for ins in finishing[-extra:]:
                ins.mem_end += 1
                if not ins.forwarded:
                    cpu.memory.free_at = ins.mem_end + 1
        elif cpu.units[unit].pipelined:
            for ins in cpu.issued:
                if ins.cls == unit and ins.ex_start is not None and ins.ex_end >= cpu.cycle:
                    ins.ex_end += 1
            cpu.units[unit].frozen_at = cpu.cycle
        else:
            for ins in finishing[-extra:]:
                cpu.units[unit].hold(ins)