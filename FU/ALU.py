from Isa import ParseError
#Function definition for ALU operations

def evaluate(ins):
    a = ins.vals[0]
    if ins.op == 'addi':
        return int(a) + ins.imm
    b = ins.vals[1]
    if ins.op == 'add':
        return int(a) + int(b)
    if ins.op == 'sub':
        return int(a) - int(b)
    # Floating point operations
    if ins.op == 'add.d':
        return a + b
    if ins.op == 'sub.d':
        return a - b
    if ins.op == 'mult':
        return int(a) * int(b)
    if ins.op == 'mult.d':
        return a * b
    #Branches Prediction 
    if ins.op == 'beq':
        return a == b
    if ins.op == 'bne':
        return a != b
    raise ParseError('cannot execute %s' % ins.op)