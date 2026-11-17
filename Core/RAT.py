class RegisterAliasTable:
    def __init__(self):
        self.tags = {}

    #who is going to write to this register? 
    def tag_of(self, reg):
        return self.tags.get(reg)

    #sets who is writing to the register
    def set(self, reg, rob_id):
        if reg == ('i', 0):
            return
        self.tags[reg] = rob_id

    #remove the entry, when an instruction commits and writes to the register
    def clear_if_tagged(self, reg, rob_id):
        if self.tags.get(reg) == rob_id:
            del self.tags[reg]

    #rebuild the RAT from the live entries in the ROB
    #called from commit, when a branch mispredict occurs and the ROB is squashed
    def rebuild(self, live_entries):
        self.tags = {}
        for e in live_entries:
            if e.dest is not None:
                self.set(e.dest, e.id)

    #just sorts the table
    def entries(self):
        return sorted(self.tags.items())

    # Bool = is everything renamed now?
    def __bool__(self):
        return bool(self.tags)