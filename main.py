import sys

from Isa import ParseError
from Inputs import parse_input
from Cpu import CPU
import report


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    trace = '--trace' in argv
    paths = [a for a in argv if not a.startswith('--')]
    if not paths:
        print('usage: python main.py <input.txt> [--trace]')
        return 1
    try:
        cfg, prog, iregs, fregs, mem = parse_input(paths[0])
    except (ParseError, OSError) as err:
        print('input error: %s' % err)
        return 1
    if not prog:
        print('no instructions found in %s' % paths[0])
        return 1
    try:
        cpu = CPU(cfg, prog, iregs, fregs, mem)
        cpu.run(on_cycle=report.print_stat if trace else None)
    except ParseError as err:
        print('runtime error: %s' % err)
        return 1
    report.print_status_table(cpu)
    report.print_results(cpu)
    return 0


if __name__ == '__main__':
    sys.exit(main())