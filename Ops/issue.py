from Isa import NOPU, BRANCHES


def run(cpu):
    #Check whether the processor is recovering from a branch misprediction
    if cpu.cycle < cpu.resume_issue_at:
        cpu.stalls[cpu.cycle] = 'mispredict recovery'
        return
    #Check whether there are more instructions to issue
    if cpu.next_issue >= len(cpu.prog):
        return
    line = cpu.prog[cpu.next_issue]
    #Check reservation station availability
    if cpu.stations.full(line.cls):
        cpu.stalls[cpu.cycle] = 'Reservation Station FUll (%s)' % line.cls
        return
    #Check ROB availability. Both need to be available for issuing 
    if cpu.rob.full():
        cpu.stalls[cpu.cycle] = 'ROB full'
        return
    #Create a new instruction instance - fresh copy from the CPU
    ins = line.fresh_copy(len(cpu.issued))
    cpu.issued.append(ins)
    cpu.history.append(ins)
    #allocate resources
    ins.issue = cpu.cycle
    ins.rob_id = cpu.rob.allocate(ins)
    cpu.stations.allocate(ins)
    #register renaming
    rename_sources(cpu, ins)
    #Update the RAT for the destination register
    if ins.dest is not None:
        cpu.rat.set(ins.dest, ins.rob_id)
        #branchr prediction
    if ins.op in BRANCHES:
        ins.predicted_next = cpu.btb.predict(ins)
        cpu.next_issue = ins.predicted_next
    else:
        cpu.next_issue += 1

#identify register dependencies (RAW)
def rename_sources(cpu, ins):
    #Look up the register in the RAT
    for pos, reg in enumerate(ins.srcs):
        tag = cpu.rat.tag_of(reg)
        #Init operand information
        ins.tags.append(None)
        ins.vals.append(None)
        ins.ready_cycle.append(None)
        #Read a register that has no pending producer
        if tag is None:
            ins.ready_cycle[pos] = 0
            ins.vals[pos] = cpu.registers.read(reg)
            continue
        #Check whether a pending producer has finished
        entry = cpu.rob.entry(tag)
        if entry.ready:
            ins.ready_cycle[pos] = entry.ins.wb
            ins.vals[pos] = entry.value
            #record the unresolved dependency
        else:
            ins.tags[pos] = tag