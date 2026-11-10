from Isa import NOPU, BRANCHES


def run(cpu):
    branch = cpu.waiting_on_branch
    if branch is not None:
        if branch.ex_end is None or branch.ex_end >= cpu.cycle:
            cpu.stalls[cpu.cycle] = 'waiting on branch'
            return
        cpu.next_issue = branch.target if branch.result else branch.idx + 1
        cpu.waiting_on_branch = None
    if cpu.next_issue >= len(cpu.prog):
        return
    line = cpu.prog[cpu.next_issue]
    if cpu.stations.full(line.cls):
        cpu.stalls[cpu.cycle] = 'RS full (%s)' % line.cls
        return
    if cpu.rob.full():
        cpu.stalls[cpu.cycle] = 'ROB full'
        return
    ins = line.fresh_copy(len(cpu.issued))
    cpu.issued.append(ins)
    ins.issue = cpu.cycle
    ins.rob_id = cpu.rob.allocate(ins)
    cpu.stations.allocate(ins)
    rename_sources(cpu, ins)
    if ins.dest is not None:
        cpu.rat.set(ins.dest, ins.rob_id)
    if ins.op in BRANCHES:
        cpu.waiting_on_branch = ins
    else:
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