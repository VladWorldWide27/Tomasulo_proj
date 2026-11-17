class RobEntry:
    def __init__(self, rid, ins):
        self.id = rid
        self.ins = ins
        self.dest = ins.dest
        self.value = None
        self.ready = False
        self.committed = False




#Holds the result until it is safe to make it permanent. Misprediction defence.

class ReorderBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = []
        self.head = 0

    #counter for the uncomitted entries. Check if there is space for another one
    def full(self):
        return sum(1 for e in self.entries if not e.committed) >= self.capacity

    # allocates a new entry, returns the rob_id of the new entry
    def allocate(self, ins):
        rid = len(self.entries)
        self.entries.append(RobEntry(rid, ins))
        return rid

    #returns the entry for a given rob_id
    def entry(self, rob_id):
        return self.entries[rob_id]

    #returns the entry at the head of the ROB. oldest uncommited entry
    def head_entry(self):
        if self.head >= len(self.entries):
            return None
        return self.entries[self.head]

    #move the head pointer one slot forward. advanced after commit 
    def retire_head(self):
        self.head += 1

    #returns active entries in the ROB. not yet committed. needed for misprediction recovery
    def live(self):
        return [e for e in self.entries[self.head:] if not e.committed]

    #deletes the entrie after the given. If the prediction was incorrect
    def squash_after(self, rob_id):
        del self.entries[rob_id + 1:]