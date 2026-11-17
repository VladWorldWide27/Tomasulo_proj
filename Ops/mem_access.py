from Isa import NOPU
from Core.cdb import MEMORY

#Check dependencies on older stores
def check_stores(cpu, load):
    #Check older stores
    for store in reversed(cpu.stations.older_stores(load)):
        #Wait for unknown store addresses
        if store.address is None:
            return 'wait', None
        #Skip stores with different addresses
        if store.address != load.address:
            continue
        #Check whether the store value is ready
        arrived = store.ready_cycle[0]
        if arrived is None or arrived >= cpu.cycle:
            return 'wait', None
        #Forward the value or access memory
        return 'forward', store
    return 'memory', None

#Free reservation stations
def release_returned_loads(cpu):
    for ins in cpu.issued:
        if ins.op == 'ld' and ins.wb is not None and ins.wb <= cpu.cycle:
            cpu.stations.release(ins)


#execute memory ops
def run(cpu):
    #Find loads ready for memory access
    for ins in cpu.issued:
        if ins.op == 'ld' and ins.ex_end is not None and ins.mem_start is None:
            if ins.ex_end >= cpu.cycle:
                continue
            #Check for store dependencies
            action, store = check_stores(cpu, ins)
            if action == 'wait':
                continue
            #store to load forwarding forwarding
            if action == 'forward':
                if cpu.cdb_room[MEMORY] == 0:
                    cpu.cdb_stalls.add((cpu.cycle, MEMORY))
                    continue
                cpu.cdb_room[MEMORY] -= 1
                ins.mem_start = cpu.cycle
                ins.mem_end = cpu.cycle
                ins.result = store.vals[0]
                ins.forwarded = True
                return
            #regular memory access
            if not cpu.memory.available(cpu.cycle):
                continue
            ##reserve a CDB slot for the forwarded value
            #unnecessary check really
            if cpu.memory.access_cycles == 1:
                #Confirm capacity
                if cpu.cdb_room[MEMORY] == 0:
                    cpu.cdb_stalls.add((cpu.cycle, MEMORY))
                    continue
                #reserve capaciry
                cpu.cdb_room[MEMORY] -= 1
                #access memory
            ins.mem_start = cpu.cycle
            ins.mem_end = cpu.memory.begin_access(cpu.cycle)
            ins.result = cpu.memory.read(ins.address)
            return
        #non FU ops
        if ins.cls == NOPU and ins.ex_end is not None and ins.mem_start is None:
            if ins.ex_end < cpu.cycle:
                ins.mem_start = cpu.cycle
                ins.mem_end = cpu.cycle