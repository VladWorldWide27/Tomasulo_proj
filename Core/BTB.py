class BranchTargetBuffer:
    def __init__(self, size=8):
        self.size = size
        self.taken = [False] * size
        self.target = [None] * size

    #use 3 bits of the word address
    def index(self, ins):
        return ins.idx % self.size

    #called at issue
    #
    def predict(self,ins):
        i = self.index(ins)
        #if taken and holds a target
        if self.taken[i] and self.target[i] is not None:
            return self.target[i]
        return ins.idx + 1

    #called from branch.run, the cycle after branch is resolved
    #sets bits to what took place, refreshes the target, when branch was taken
    def update(self, ins):
        i = self.index(ins)
        self.taken[i] = bool(ins.result)
        if ins.result:
            self.target[i] = ins.target