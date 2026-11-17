from Isa import INT ,FPA, FPM, BRANCHES

MEMORY = 'memory'

#determines where the answer is coming from
def cdb_unit(ins):
    if ins.op == 'ld':
        return MEMORY
    if ins.cls in (INT, FPA, FPM) and ins.op not in BRANCHES:
        return ins.cls
    return None

#when is the result ready to be written back to the CDB.
#Buffer accounting
def finish_cycle(ins):
    return ins.mem_end if ins.op == 'ld' else ins.ex_end


class CommonDataBus:
    def __init__(self, buffer_entries):
        self.buffer_entries = buffer_entries
        self.log = {}

    #Returns the instruction that wins arbitration
    def arbitrate(self, requesters):
        if not requesters:
            return None
        return min(requesters, key=lambda ins: ins.seq)

    #Hands the Bus over. write back calles it. Fills the W column of the report
    def grant(self, ins, cycle):
        ins.wb = cycle
        self.log[cycle] = ins.idx + 1

    #Hands the  result to every waiting instruction at once, 
    def broadcast(self, program, rob_id, value, cycle):
        for ins in program:
            #if it hasn't issued yet: skip it
            if ins.issue is None:
                continue
            for pos, tag in enumerate(ins.tags):
                # if that slot's tag == the ROB id just broadcast:
                if tag == rob_id:
                    ins.tags[pos] = None
                    ins.ready_cycle[pos] = cycle
                    ins.vals[pos] = value