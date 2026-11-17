from Isa import NOPU, BRANCHES, ParseError
from FU import ALU
from Core.cdb import cdb_unit

#identify which operands are needed for the instruction
def operand_positions(ins):
    if ins.cls == NOPU:
        return []
    if ins.op == 'ld':
        return [0]
    if ins.op == 'sd':
        return [1]
    return list(range(len(ins.srcs)))

#determine when the execution can begin
def earliest_start(ins):
    #issue cycle
    times = [ins.issue]
    #operand availability check
    for pos in operand_positions(ins):
        ready = ins.ready_cycle[pos]
        if ready is None:
            return None
        times.append(ready)
        #earliest execution start is the cycle after the last operand is ready
    return max(times) + 1


def run(cpu):
    #check issued instructions
    for ins in cpu.issued:
        if ins.issue is None or ins.ex_start is not None or ins.commit is not None:
            continue
        #enforce a delay
        if ins.issue >= cpu.cycle:
            continue
        #check RAW dependencies
        start = earliest_start(ins)
        if start is None or cpu.cycle < start:
            continue
        #check whether there is an older branch that has not finished execution before the current cycle
        if any(b.op in BRANCHES and b.seq < ins.seq
               and (b.ex_end is None or b.ex_end >= cpu.cycle)
               for b in cpu.issued):
            continue
        #hanlde instructions that do not need FU( same cycle execution)
        if ins.cls == NOPU:
            ins.ex_start = cpu.cycle
            ins.ex_end = cpu.cycle
            continue
        #Check FU availability
        unit = cpu.units[ins.cls]
        if not unit.can_accept(cpu.cycle):
            continue
        #check CDB availability
        if cdb_unit(ins) == ins.cls and unit.ex_cycles == 1:
            if cpu.cdb_room[ins.cls] == 0:
                cpu.cdb_stalls.add((cpu.cycle, ins.cls)) #not available, stall the instruction
                continue
            cpu.cdb_room[ins.cls] -= 1 #available, delay
            #start execution
        ins.ex_start = cpu.cycle
        ins.ex_end = unit.accept(cpu.cycle)
        #execute adress calculations  base reg + imm offset
        if ins.op in ('ld', 'sd'):
            base = ins.vals[0 if ins.op == 'ld' else 1]
            ins.address = int(base) + ins.imm
            #check mem address
            try:
                cpu.memory.check(ins.address)
            except ParseError as err:
                ins.fault = err
        else:
            #calc ALU
            ins.result = ALU.evaluate(ins)