class RegisterAliasTable:
    def __init__(self):
        self.tags = {}

    def tag_of(self, reg):
        return self.tags.get(reg)

    def set(self, reg, rob_id):
        self.tags[reg] = rob_id

    def clear_if_tagged(self, reg, rob_id):
        if self.tags.get(reg) == rob_id:
            del self.tags[reg]

    def entries(self):
        return sorted(self.tags.items())

    def __bool__(self):
        return bool(self.tags)