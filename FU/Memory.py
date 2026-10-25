from isa import MEM_BYTES, ParseError


class DataMemory:
    def __init__(self, initial, access_cycles):
        self.access_cycles = access_cycles
        self.free_at = 1
        self.words = {}
        for addr, value in initial.items():
            self.check(addr)
            self.words[addr] = value

    def check(self, addr):
        if addr < 0 or addr >= MEM_BYTES:
            raise ParseError('address %d outside %dB memory' % (addr, MEM_BYTES))
        if addr % 4 != 0:
            raise ParseError('address %d is not word aligned' % addr)

    def available(self, cycle):
        return self.free_at <= cycle

    def begin_access(self, cycle):
        end = cycle + self.access_cycles - 1
        self.free_at = end + 1
        return end

    def read(self, addr):
        return self.words.get(addr, 0.0)

    def write(self, addr, value):
        self.words[addr] = value

    def nonzero(self):
        return [(a, self.words[a]) for a in sorted(self.words) if self.words[a] != 0]