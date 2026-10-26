def finish_cycle(ins):
    if ins.op == 'sd':
        if ins.ex_end is None or ins.ready_cycle[0] is None:
            return None
        return max(ins.ex_end, ins.ready_cycle[0])
    return ins.wb


def run(cpu):
    entry = cpu.rob.head_entry()
    if entry is None:
        return
    ins = entry.ins
    done = finish_cycle(ins)
    if done is None or done >= cpu.cycle:
        return
    ins.commit = cpu.cycle
    entry.committed = True
    if ins.op == 'sd':
        cpu.memory.write(ins.address, ins.vals[0])
        cpu.stations.release(ins)
    else:
        if ins.dest is not None: 
            cpu.registers.write(ins.dest, entry.value)
    if ins.dest is not None:
        cpu.rat.clear_if_tagged(ins.dest, entry.id)
    cpu.rob.retire_head()