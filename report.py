import sys

from Isa import INT, FPA, FPM, LSU, reg_name


def fmt(v):
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        return ('%.6f' % v).rstrip('0')
    return str(v)


def span(a, b):
    if a is None:
        return '-'
    return str(a) if a == b else '%d-%d' % (a, b)


def print_status_table(cpu, out=sys.stdout, tsv=False):
    head = ['#', 'Inst', 'OP', 'I', 'E', 'M', 'W', 'C']
    rows = []
    for row, ins in enumerate(cpu.prog, 1):
        rows.append([
            str(row),
            str(ins.idx + 1),
            opcode(ins),
            str(ins.issue) if ins.issue else '-',
            span(ins.ex_start, ins.ex_end),
            span(ins.mem_start, ins.mem_end) if ins.op == 'ld' else '-',
            str(ins.wb) if ins.wb else '-',
            str(ins.commit) if ins.commit else '-',
        ])
    if tsv:
        print('\t'.join(head), file=out)
        for r in rows:
            print('\t'.join(r), file=out)
        return
    width = [max(len(r[c]) for r in rows + [head]) for c in range(len(head))]
    line = '  '.join('%-*s' % (width[c], head[c]) for c in range(len(head)))
    print(line, file=out)
    print('-' * len(line), file=out)
    for r in rows:
        print('  '.join('%-*s' % (width[c], r[c]) for c in range(len(head))), file=out)


def opcode(ins):
    return ins.text.split()[0]

def print_results(cpu, out=sys.stdout):
    print(file=out)
    print('REGISTER VALUES', file=out)
    used_i = cpu.registers.nonzero_int()
    used_f = cpu.registers.nonzero_fp()
    if used_i:
        print(' '.join('%8s' % ('R%d' % n) for n in used_i), file=out)
        print(' '.join('%8s' % cpu.registers.ireg[('i', n)] for n in used_i), file=out)
    if used_f:
        print(' '.join('%8s' % ('F%d' % n) for n in used_f), file=out)
        print(' '.join('%8s' % fmt(cpu.registers.freg[('f', n)]) for n in used_f), file=out)
    print(file=out)
    print('NON-ZERO MEMORY VALUES', file=out)
    print('%-10s %s' % ('Addresses', 'Values'), file=out)
    for addr, value in cpu.memory.nonzero():
        print('%-10d %s' % (addr, fmt(value)), file=out)
    print(file=out)
    print('Total cycles: %d' % max(i.commit for i in cpu.prog), file=out)
    if cpu.stalls:
        print('Issue stalls: %s' % ', '.join(
            'c%d %s' % (c, r) for c, r in sorted(cpu.stalls.items())), file=out)


def print_stat(cpu, out=sys.stdout):
    print('=== cycle %d ===' % cpu.cycle, file=out)
    print('RS in use: ' + ', '.join('%s %d/%d' % ((c,) + cpu.stations.occupancy(c))
                                    for c in (INT, FPA, FPM, LSU)), file=out)
    for e in cpu.rob.live():
        i = e.ins
        print('  ROB%-3d %-20s dest=%-4s val=%-10s ready=%s' % (
            e.id + 1, i.text, reg_name(i.dest) if i.dest else '-',
            fmt(e.value) if e.value is not None else '-',
            'Y' if e.ready else 'N'), file=out)
    if cpu.rat:
        print('  RAT: ' + ', '.join('%s->ROB%d' % (reg_name(r), t + 1)
                                    for r, t in cpu.rat.entries()), file=out)
    print(file=out)