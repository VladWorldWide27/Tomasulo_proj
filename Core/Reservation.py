from Isa import NOPU


class ReservationStations:
    def __init__(self, capacity):
        self.capacity = dict(capacity)
        self.used = {cls: 0 for cls in capacity}
        self.pending = []

    def full(self, cls):
        if cls == NOPU:
            return False
        return self.used.get(cls, 0) >= self.capacity.get(cls, 0)

    def allocate(self, cls):
        if cls != NOPU:
            self.used[cls] += 1

    def release(self, ins):
        if ins.rs_released or ins.cls == NOPU:
            return
        ins.rs_released = True
        self.pending.append(ins.cls)

    def tick(self):
        for cls in self.pending:
            self.used[cls] -= 1
        self.pending = []

    def occupancy(self, cls):
        return self.used.get(cls, 0), self.capacity.get(cls, 0)