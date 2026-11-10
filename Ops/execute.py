from Isa import NOPU, ParseError
from FU import ALU
from Core.cdb import cdb_unit

def operand_positions(ins):
    if ins.cls == NOPU:
        return []
    if ins.op == 'ld':
        return [0]
    if ins.op == 'sd':
        return [1]
    return list(range(len(ins.srcs)))


def earliest_start(ins):
    times = [ins.issue]
    for pos in operand_positions(ins):
        ready = ins.ready_cycle[pos]
        if ready is None:
            return None
        times.append(ready)
    return max(times) + 1


def run(cpu):
    for ins in cpu.issued:
        if ins.issue is None or ins.ex_start is not None or ins.commit is not None:
            continue
        if ins.issue >= cpu.cycle:
            continue
        start = earliest_start(ins)
        if start is None or cpu.cycle < start:
            continue
        if ins.cls == NOPU:
            ins.ex_start = cpu.cycle
            ins.ex_end = cpu.cycle
            continue
        unit = cpu.units[ins.cls]
        if not unit.can_accept(cpu.cycle):
            continue
        if cdb_unit(ins) == ins.cls and unit.ex_cycles == 1:
            if cpu.cdb_room[ins.cls] == 0:
                cpu.cdb_stalls.add((cpu.cycle, ins.cls))
                continue
            cpu.cdb_room[ins.cls] -= 1
        ins.ex_start = cpu.cycle
        ins.ex_end = unit.accept(cpu.cycle)
        if ins.op in ('ld', 'sd'):
            base = ins.vals[0 if ins.op == 'ld' else 1]
            ins.address = int(base) + ins.imm
            try:
                cpu.memory.check(ins.address)
            except ParseError as err:
                ins.fault = err
        else:
            ins.result = ALU.evaluate(ins)