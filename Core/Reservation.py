from Isa import NOPU,LSU

#Counts how many reservation stations each unit has in use, and separately keeps the load/store queue in program order.
class ReservationStations:
    def __init__(self, capacity):
        self.capacity = dict(capacity)
        self.used = {cls: 0 for cls in capacity}
        self.pending = []
        self.lsqueue = []

    #check whether the reservation station for a given class is full. If it is, the instruction cannot be issued=
    def full(self, cls):
        if cls == NOPU:
            return False
        return self.used.get(cls, 0) >= self.capacity.get(cls, 0)

    #Bump the count of used reservation stations.  append it to the load and store queue. Called at issue
    def allocate(self, ins):
        if ins.cls == NOPU:
            return
        self.used[ins.cls] += 1
        if ins.cls == LSU:
            self.lsqueue.append(ins)

    #Marks the station as free. Puts it in a pending list to be decremented at the end of the cycle. Called at writeback.
    def release(self, ins):
        if ins.rs_released or ins.cls == NOPU:
            return
        ins.rs_released = True
        self.pending.append(ins.cls)

        if ins.cls == LSU:
            self.lsqueue.remove(ins)

    #Applies everything that is pending, then clears
    def tick(self):
        for cls in self.pending:
            self.used[cls] -= 1
        self.pending = []

    #Walks the queue and returns the stores that come before the given load.  Used to check for forwarding. Called in mem_access
    def older_stores(self,load):
        stores = []
        for ins in self.lsqueue:
            if ins is load:
                break
            if ins.op == 'sd':
                stores.append(ins)
        return stores   

    #debug feature. returns the number of used and total reservation stations for each class
    def occupancy(self, cls):
        return self.used.get(cls, 0), self.capacity.get(cls, 0)