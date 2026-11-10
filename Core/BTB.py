class BranchTargetBuffer:
    def __init__(self, size=8):
        self.size = size
        self.taken = [False] * size
        self.target = [None] * size

    def index(self, ins):
        return ins.idx % self.size

    def predict(self,ins):
        i = self.index(ins)
        if self.taken[i] and self.target[i] is not None:
            return self.target[i]
        return ins.idx + 1

    def update(self, ins):
        i = self.index(ins)
        self.taken[i] = bool(ins.result)
        if ins.result:
            self.target[i] = ins.target