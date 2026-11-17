from Isa import BRANCHES

#ensure that all the necessary work has finished before committing the instruction
def finish_cycle(ins):
    if ins.op in BRANCHES:
        return ins.ex_end
    #store is different because the memory adress needs to be calculated and the value needs to be available 
    if ins.op == 'sd':
        if ins.ex_end is None or ins.ready_cycle[0] is None:
            return None
        return max(ins.ex_end, ins.ready_cycle[0])
    #other instructions write back cycle
    return ins.wb


def run(cpu):
    #get the oldest instruction in the ROB
    entry = cpu.rob.head_entry()
    if entry is None:
        return
    #check if the instruction is ready to commit
    ins = entry.ins
    done = finish_cycle(ins)
    if done is None or done >= cpu.cycle:
        return
    #check if the instruction has any exceptions
    if ins.fault is not None:
        raise ins.fault
    #mark intruction as committed and update the state of the CPU
    ins.commit = cpu.cycle
    entry.committed = True
    #update processor state
    #store updates memory when commits. Value -> memory 
    if ins.op == 'sd':
        cpu.memory.write(ins.address, ins.vals[0])
        cpu.stations.release(ins)
        #for branch release reservation station
    elif ins.op in BRANCHES:
        cpu.stations.release(ins)
    else:
        #ALU instructions
        #Calculate result during exec and write back to ROB/CDB 
        if ins.dest is not None: 
            cpu.registers.write(ins.dest, entry.value)
            #clear RAT
    if ins.dest is not None:
        cpu.rat.clear_if_tagged(ins.dest, entry.id)
        #remove the instruction from the ROB
    cpu.rob.retire_head()