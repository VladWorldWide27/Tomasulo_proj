class RobEntry:
    def __init__(self, rid, ins):
        self.id = rid
        self.ins = ins
        self.dest = ins.dest
        self.value = None
        self.ready = False
        self.committed = False