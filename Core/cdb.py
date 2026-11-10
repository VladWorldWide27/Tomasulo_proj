from Isa import INT ,FPA, FPM, BRANCHES

MEMORY = 'memory'

def cdb_unit(ins):
    if ins.op == 'ld':
        return MEMORY
    if ins.cls in (INT, FPA, FPM) and ins.op not in BRANCHES:
        return ins.cls
    return None

def finish_cycle(ins):
    return ins.mem_end if ins.op == 'ld' else ins.ex_end

class CommonDataBus:
    def __init__(self, buffer_entries):
        self.buffer_entries = buffer_entries
        self.log = {}

    def arbitrate(self, requesters):
        if not requesters:
            return None
        return min(requesters, key=lambda ins: ins.seq)

    def grant(self, ins, cycle):
        ins.wb = cycle
        self.log[cycle] = ins.idx + 1

    def broadcast(self, program, rob_id, value, cycle):
        for ins in program:
            if ins.issue is None:
                continue
            for pos, tag in enumerate(ins.tags):
                if tag == rob_id:
                    ins.tags[pos] = None
                    ins.ready_cycle[pos] = cycle
                    ins.vals[pos] = value