from Isa import NOPU


def check_stores(cpu, load):
    for store in reversed(cpu.stations.older_stores(load)):
        if store.address is None:
            return 'wait', None
        if store.address != load.address:
            continue
        arrived = store.ready_cycle[0]
        if arrived is None or arrived >= cpu.cycle:
            return 'wait', None
        return 'forward', store
    return 'memory', None

def release_returned_loads(cpu):
    for ins in cpu.issued:
        if ins.op == 'ld' and ins.mem_end is not None and ins.mem_end <= cpu.cycle:
            cpu.stations.release(ins)


def run(cpu):
    for ins in cpu.issued:
        if ins.op == 'ld' and ins.ex_end is not None and ins.mem_start is None:
            if ins.ex_end >= cpu.cycle:
                continue
            action, store = check_stores(cpu, ins)
            if action == 'wait':
                continue
            if action == 'forward':
                ins.mem_start = cpu.cycle
                ins.mem_end = cpu.cycle
                ins.result = store.vals[0]
                return
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