from Isa import ParseError


def evaluate(ins):
    a = ins.vals[0]
    if ins.op == 'addi':
        return int(a) + ins.imm
    b = ins.vals[1]
    if ins.op == 'add':
        return int(a) + int(b)
    if ins.op == 'sub':
        return int(a) - int(b)
    if ins.op == 'add.d':
        return a + b
    if ins.op == 'sub.d':
        return a - b
    if ins.op == 'mult':
        return int(a) * int(b)
    if ins.op == 'mult.d':
        return a * b
    raise ParseError('cannot execute %s' % ins.op)