class RobEntry:
    def __init__(self, rid, ins):
        self.id = rid
        self.ins = ins
        self.dest = ins.dest
        self.value = None
        self.ready = False
        self.committed = False


class ReorderBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = []
        self.head = 0

    def full(self):
        return sum(1 for e in self.entries if not e.committed) >= self.capacity

    def allocate(self, ins):
        rid = len(self.entries)
        self.entries.append(RobEntry(rid, ins))
        return rid

    def entry(self, rob_id):
        return self.entries[rob_id]

    def head_entry(self):
        if self.head >= len(self.entries):
            return None
        return self.entries[self.head]

    def retire_head(self):
        self.head += 1

    def live(self):
        return [e for e in self.entries[self.head:] if not e.committed]