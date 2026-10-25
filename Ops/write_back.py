from Isa import NOPU


def completed(ins, cycle):
    if ins.op == 'ld' or ins.cls == NOPU:
        return ins.mem_end is not None and ins.mem_end < cycle
    return ins.ex_end is not None and ins.ex_end < cycle


def run(cpu):
    requesters = [ins for ins in cpu.prog
                  if ins.wb is None and ins.op != 'sd' and completed(ins, cpu.cycle)]
    winner = cpu.cdb.arbitrate(requesters)
    if winner is None:
        return
    cpu.cdb.grant(winner, cpu.cycle)
    entry = cpu.rob.entry(winner.rob_id)
    entry.value = winner.result
    entry.ready = True
    if winner.op != 'ld':
        cpu.stations.release(winner)
    cpu.cdb.broadcast(cpu.prog, winner.rob_id, winner.result, cpu.cycle)