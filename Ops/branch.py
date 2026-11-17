from Isa import BRANCHES

def run(cpu):
    #find branches that just finished execution in the last cycle
    for ins in cpu.issued:
        if ins.op not in BRANCHES or ins.ex_end != cpu.cycle - 1:
            continue
        #branch predictor upd
        cpu.btb.update(ins)
        #correct next instruction
        actual = ins.target if ins.result else ins.idx + 1
        #check the prediction
        if actual == ins.predicted_next:
            continue
        #misprediction recovery
        squash_after(cpu, ins)
        cpu.next_issue = actual
        cpu.resume_issue_at = cpu.cycle + 1
        return

def squash_after(cpu, branch):
    #identify what needs to be flushed
    wrong = [i for i in cpu.issued if i.seq > branch.seq]
    #reset the state of the flushed instructions/ release the resources
    for ins in wrong:
        cpu.stations.release(ins)
        ins.tags = [None] * len(ins.tags)
        ins.flushed = cpu.cycle
    #remove the flushed instructions from the issued list, ROB, and RAT
    cpu.issued = [i for i in cpu.issued if i.seq <= branch.seq]
    cpu.rob.squash_after(branch.rob_id)
    cpu.rat.rebuild(cpu.rob.live())
    #record the misprediction for reporting
    cpu.mispredicts.append((branch.ex_end, branch, wrong))