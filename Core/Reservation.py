from Isa import NOPU,LSU


class ReservationStations:
    def __init__(self, capacity):
        self.capacity = dict(capacity)
        self.used = {cls: 0 for cls in capacity}
        self.pending = []
        self.lsqueue = []

    def full(self, cls):
        if cls == NOPU:
            return False
        return self.used.get(cls, 0) >= self.capacity.get(cls, 0)

    def allocate(self, ins):
        if ins.cls == NOPU:
            return
        self.used[ins.cls] += 1
        if ins.cls == LSU:
            self.lsqueue.append(ins)

    def release(self, ins):
        if ins.rs_released or ins.cls == NOPU:
            return
        ins.rs_released = True
        self.pending.append(ins.cls)

        if ins.cls == LSU:
            self.lsqueue.remove(ins)

    def tick(self):
        for cls in self.pending:
            self.used[cls] -= 1
        self.pending = []

    def older_stores(self,load):
        stores = []
        for ins in self.lsqueue:
            if ins is load:
                break
            if ins.op == 'sd':
                stores.append(ins)
        return stores

    def tick(self):
        for cls in self.pending:
            self.used[cls] -= 1
        self.pending = []    

    def occupancy(self, cls):
        return self.used.get(cls, 0), self.capacity.get(cls, 0)