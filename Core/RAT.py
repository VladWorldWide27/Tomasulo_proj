class RegisterAliasTable:
    def __init__(self):
        self.tags = {}

    def tag_of(self, reg):
        return self.tags.get(reg)

    def set(self, reg, rob_id):
        if reg == ('i', 0):
            return
        self.tags[reg] = rob_id

    def clear_if_tagged(self, reg, rob_id):
        if self.tags.get(reg) == rob_id:
            del self.tags[reg]

    def rebuild(self, live_entries):
        self.tags = {}
        for e in live_entries:
            if e.dest is not None:
                self.set(e.dest, e.id)

    def entries(self):
        return sorted(self.tags.items())

    def __bool__(self):
        return bool(self.tags)