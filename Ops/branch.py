from Isa import BRANCHES

def run(cpu):
    for ins in cpu.issued:
        if ins.op not in BRANCHES or ins.ex_end != cpu.cycle - 1:
            continue
        cpu.btb.update(ins)
        actual = ins.target if ins.result else ins.idx + 1
        if actual == ins.predicted_next:
            continue
        squash_after(cpu, ins)
        cpu.next_issue = actual
        cpu.resume_issue_at = cpu.cycle + 1
        return

def squash_after(cpu, branch):
    wrong = [i for i in cpu.issued if i.seq > branch.seq]
    for ins in wrong:
        cpu.stations.release(ins)
        ins.tags = [None] * len(ins.tags)
        ins.flushed = cpu.cycle
    cpu.issued = [i for i in cpu.issued if i.seq <= branch.seq]
    cpu.rob.squash_after(branch.rob_id)
    cpu.rat.rebuild(cpu.rob.live())
    cpu.mispredicts.append((branch.ex_end, branch, wrong))