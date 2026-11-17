from Isa import MEM_BYTES, ParseError


class DataMemory:
    def __init__(self, initial, access_cycles):
        self.access_cycles = access_cycles
        self.free_at = 1
        self.words = {}
        for addr, value in initial.items():
            self.check(addr)
            self.words[addr] = value

    #called in execute to check if the address is valid before starting the access
    def check(self, addr):
        if addr < 0 or addr >= MEM_BYTES:
            raise ParseError('address %d outside %dB memory' % (addr, MEM_BYTES))
        if addr % 4 != 0:
            raise ParseError('address %d is not word aligned' % addr)

    #check if the port is free    
    def available(self, cycle):
        return self.free_at <= cycle

    #begin the access, return the cycle when it will be done
    def begin_access(self, cycle):
        end = cycle + self.access_cycles - 1
        self.free_at = end + 1
        return end

    #returns the value at the address, or 0 if it has not been written yet
    def read(self, addr):
        return self.words.get(addr, 0.0)

    #write the value to the address, called in commit
    def write(self, addr, value):
        self.words[addr] = value

    #sorted list of (address, value) pairs for all mem locations
    def nonzero(self):
        return [(a, self.words[a]) for a in sorted(self.words) if self.words[a] != 0]