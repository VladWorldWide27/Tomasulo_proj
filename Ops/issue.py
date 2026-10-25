from Isa import NOPU


def run(cpu):
    if cpu.next_issue >= len(cpu.prog):
        return
    ins = cpu.prog[cpu.next_issue]
    if cpu.stations.full(ins.cls):
        cpu.stalls[cpu.cycle] = 'RS full (%s)' % ins.cls
        return
    if cpu.rob.full():
        cpu.stalls[cpu.cycle] = 'ROB full'
        return
    ins.issue = cpu.cycle
    ins.rob_id = cpu.rob.allocate(ins)
    cpu.stations.allocate(ins.cls)
    rename_sources(cpu, ins)
    if ins.dest is not None:
        cpu.rat.set(ins.dest, ins.rob_id)
    cpu.next_issue += 1


def rename_sources(cpu, ins):
    for pos, reg in enumerate(ins.srcs):
        tag = cpu.rat.tag_of(reg)
        ins.tags.append(None)
        ins.vals.append(None)
        ins.ready_cycle.append(None)
        if tag is None:
            ins.ready_cycle[pos] = 0
            ins.vals[pos] = cpu.registers.read(reg)
            continue
        entry = cpu.rob.entry(tag)
        if entry.ready:
            ins.ready_cycle[pos] = entry.ins.wb
            ins.vals[pos] = entry.value
        else:
            ins.tags[pos] = tag