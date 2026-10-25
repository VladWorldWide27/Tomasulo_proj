import re

from Isa import Instruction, OP_CLASS, ParseError, parse_reg
from config import Config, UNIT_ALIAS


def parse_input(path):
    cfg = Config()
    iregs = {}
    fregs = {}
    mem = {}
    raw = []
    for line in open(path):
        line = line.split('#')[0].strip()
        if not line:
            continue
        low = line.lower()
        unit = None
        if ':' in line:
            head, tail = line.split(':', 1)
            key = head.strip().lower().replace('-', '_')
            if key in UNIT_ALIAS:
                unit = UNIT_ALIAS[key]
                for part in tail.split(','):
                    if '=' not in part:
                        continue
                    k, v = part.split('=', 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if k == 'rs':
                        cfg.rs[unit] = int(v)
                    elif k == 'ex':
                        cfg.ex[unit] = int(v)
                    elif k in ('fu', 'fus'):
                        cfg.fu[unit] = int(v)
                    elif k == 'mem':
                        cfg.mem_cycles = int(v)
                    elif k in ('piped', 'pipelined'):
                        cfg.pipelined[unit] = v.lower() in ('1', 'true', 'yes')
                continue
        if low.startswith('rob'):
            cfg.rob = int(re.search(r'(\d+)', line).group(1))
            continue
        if low.startswith('cdb'):
            cfg.cdb_buffer = int(re.search(r'(\d+)', line).group(1))
            continue
        if re.match(r'^mem\s*\[', low):
            for part in re.finditer(r'[Mm]em\s*\[\s*(\d+)\s*\]\s*=\s*(-?[\d.]+)', line):
                mem[int(part.group(1))] = float(part.group(2))
            continue
        if re.match(r'^[RrFf]\d+\s*=', line):
            for part in re.finditer(r'([RrFf])(\d+)\s*=\s*(-?[\d.]+)', line):
                num = int(part.group(2))
                val = part.group(3)
                if part.group(1).lower() == 'r':
                    iregs[('i', num)] = int(float(val))
                else:
                    fregs[('f', num)] = float(val)
            continue
        raw.append(line)
    prog = [build_instruction(i, t) for i, t in enumerate(raw)]
    return cfg, prog, iregs, fregs, mem


def build_instruction(idx, text):
    parts = text.replace(',', ' ').split()
    op = parts[0].lower()
    if op not in OP_CLASS:
        raise ParseError('unknown opcode: %s' % parts[0])
    ins = Instruction(idx, op, text)
    if op == 'nop':
        return ins
    if op in ('ld', 'sd'):
        m = re.match(r'\s*\w+\.?\w*\s+([RrFf]\d+)\s*,?\s*(-?\d+)\s*\(\s*([RrFf]\d+)\s*\)', text)
        if not m:
            raise ParseError('bad memory instruction: %s' % text)
        ins.imm = int(m.group(2))
        ins.base = parse_reg(m.group(3))
        if op == 'ld':
            ins.dest = parse_reg(m.group(1))
            ins.srcs = [ins.base]
        else:
            ins.srcs = [parse_reg(m.group(1)), ins.base]
        return ins
    if op in ('beq', 'bne'):
        raise ParseError('branches are not supported in this build: %s' % text)
    if op == 'addi':
        ins.dest = parse_reg(parts[1])
        ins.srcs = [parse_reg(parts[2])]
        ins.imm = int(parts[3])
        return ins
    ins.dest = parse_reg(parts[1])
    ins.srcs = [parse_reg(parts[2]), parse_reg(parts[3])]
    return ins