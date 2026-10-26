from Isa import NOPU


def blocking_store(cpu, load):
    for other in cpu.prog[:load.idx]:
        if other.op != 'sd' or other.commit is not None or other.issue is None:
            continue
        if other.address is None or other.address == load.address:
            return True
    return False

def release_returned_loads(cpu):
    for ins in cpu.prog:
        if ins.op == 'ld' and ins.mem_end is not None and ins.mem_end < cpu.cycle:
            cpu.stations.release(ins)


def run(cpu):
    release_returned_loads(cpu)
    for ins in cpu.prog:
        if ins.op == 'ld' and ins.ex_end is not None and ins.mem_start is None:
            if ins.ex_end >= cpu.cycle:
                continue
            if blocking_store(cpu, ins):
                continue
            if not cpu.memory.available(cpu.cycle):
                continue
            ins.mem_start = cpu.cycle
            ins.mem_end = cpu.memory.begin_access(cpu.cycle)
            ins.result = cpu.memory.read(ins.address)
            return
        if ins.cls == NOPU and ins.ex_end is not None and ins.mem_start is None:
            if ins.ex_end < cpu.cycle:
                ins.mem_start = cpu.cycle
                ins.mem_end = cpu.cycle