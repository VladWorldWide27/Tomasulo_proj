from Isa import NOPU, BRANCHES, INT , FPA, FPM
from Core.cdb import MEMORY, cdb_unit, finish_cycle

#check whether an instruction has finished
def completed(ins, cycle):
    #non FU ops
    if ins.op == 'ld' or ins.cls == NOPU:
        return ins.mem_end is not None and ins.mem_end < cycle
    #arithmetic ops
    return ins.ex_end is not None and ins.ex_end < cycle

#Find instructions requesting the CDB
def run(cpu):
    requesters = [ins for ins in cpu.issued
                  if ins.wb is None and ins.op != 'sd' and ins.op not in BRANCHES
                  and completed(ins, cpu.cycle)]
    #Select the CDB winner
    winner = cpu.cdb.arbitrate(requesters)
    #Grant CDB access
    if winner is not None:
        cpu.cdb.grant(winner, cpu.cycle)
        #Update ROB
        entry = cpu.rob.entry(winner.rob_id)
        entry.value = winner.result
        entry.ready = True
        #Release the reservation station
        if winner.op != 'ld':
            cpu.stations.release(winner)
            #forward the result
        cpu.cdb.broadcast(cpu.issued, winner.rob_id, winner.result, cpu.cycle)
        #additional safety for lost instructions
    check_buffers(cpu, [i for i in requesters if i is not winner])

#init CDB room for each functional unit type
def check_buffers(cpu, losers):
    cpu.cdb_room = {}
    for unit in (INT, FPA, FPM, MEMORY):
        #calc buffer capacity
        copies = 1 if unit == MEMORY else cpu.cfg.fu[unit]
        capacity = copies * (cpu.cdb.buffer_entries + 1)
        #Count instructions waiting for the CDB
        waiting = [i for i in losers if cdb_unit(i) == unit]
        #count instructions finishing during the current cycle
        finishing = [i for i in cpu.issued
                     if cdb_unit(i) == unit and finish_cycle(i) == cpu.cycle]
        #calc overflow and remaining room
        extra = len(waiting) + len(finishing) - capacity
        cpu.cdb_room[unit] = max(0, -extra)
        #cbd stall
        if extra <= 0:
            continue
        cpu.cdb_stalls.add((cpu.cycle, unit))
        #delay producing another result when no space
        if unit == MEMORY:
            for ins in finishing[-extra:]:
                ins.mem_end += 1
                if not ins.forwarded:
                    cpu.memory.free_at = ins.mem_end + 1
                    #congestion resolution
        elif cpu.units[unit].pipelined:
            for ins in cpu.issued:
                if ins.cls == unit and ins.ex_start is not None and ins.ex_end >= cpu.cycle:
                    ins.ex_end += 1
            cpu.units[unit].frozen_at = cpu.cycle
            #non pipelined FUs
        else:
            for ins in finishing[-extra:]:
                cpu.units[unit].hold(ins)