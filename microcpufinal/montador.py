"""Montador e modelo de referência da micro-CPU (versão final).

Formato (16 bits):  [15..12] opcode | [11..10] RA | [9..8] RB | [7..6] RD | [5..0] endereço  (ou [3..0] valor)

Uso:  python montador.py programa.asm programa.mif
"""
import re, sys

OPS = {'CMP': 0, 'MOVR': 1, 'MOVI': 2, 'RST': 3,
       'ADD': 4, 'SUB': 5, 'MUL': 6, 'DIV': 7,
       'ADDI': 8, 'SUBI': 9, 'MULI': 10, 'DIVI': 11,
       'JMP': 12, 'JMPR': 13, 'JZ': 14, 'JE': 15}

def reg(t):
    m = re.fullmatch(r'R([0-3])', t.upper())
    return int(m.group(1)) if m else None

def num(t):
    t = t.strip()
    return int(t, 16) if t.lower().startswith('0x') else int(t)

def word(op, ra=0, rb=0, rd=0, low=0):
    return (op << 12) | (ra << 10) | (rb << 8) | (rd << 6) | low

def assemble_line(line):
    """returns (word, normalized text) or None for empty lines"""
    code = line.split(';')[0].strip()
    if not code:
        return None
    m = re.match(r'^(\d+)\s*:\s*(.*)$', code)          # optional "NN:" address prefix (ignored, just for reading)
    if m:
        code = m.group(2)
    parts = code.replace(',', ' ').split()
    mn, args = parts[0].upper(), parts[1:]
    if mn == 'NOP':
        return word(0)
    if mn == 'RST':
        return word(OPS['RST'])
    if mn == 'CMP':
        return word(OPS['CMP'], reg(args[0]), reg(args[1]))
    if mn == 'MOV':
        src, dst = args
        if reg(src) is not None:
            return word(OPS['MOVR'], ra=reg(src), rd=reg(dst))
        v = num(src); assert 0 <= v <= 15, 'valor fora de 0..15: %s' % line
        return word(OPS['MOVI'], rd=reg(dst), low=v)
    if mn in ('ADD', 'SUB', 'MUL', 'DIV'):
        a, b, d = args
        if reg(b) is not None:
            return word(OPS[mn], reg(a), reg(b), reg(d))
        v = num(b); assert 0 <= v <= 15, 'valor fora de 0..15: %s' % line
        return word(OPS[mn + 'I'], ra=reg(a), rd=reg(d), low=v)
    if mn == 'JMP':
        if reg(args[0]) is not None:
            return word(OPS['JMPR'], ra=reg(args[0]))
        return word(OPS['JMP'], low=num(args[0]) & 63)
    if mn == 'JZ':
        return word(OPS['JZ'], ra=reg(args[0]), low=num(args[1]) & 63)
    if mn == 'JE':
        return word(OPS['JE'], low=num(args[0]) & 63)
    raise ValueError('instrução desconhecida: ' + line)

def assemble(text):
    words, src = [], []
    for ln in text.splitlines():
        w = assemble_line(ln)
        if w is not None:
            words.append(w); src.append(ln.split(';')[0].strip())
    return words, src

def to_mif(words, lines, comments=None):
    out = ['-- Programa da micro-CPU (gerado pelo montador)',
           '-- Formato: [15..12] opcode | [11..10] RA | [9..8] RB | [7..6] RD | [5..0] endereco ou [3..0] valor',
           '', 'WIDTH=16;', 'DEPTH=64;', '', 'ADDRESS_RADIX=UNS;', 'DATA_RADIX=HEX;', '', 'CONTENT BEGIN']
    for i, w in enumerate(words):
        c = comments[i] if comments else lines[i]
        out.append('    %-3d :   %04X;   -- %s' % (i, w, c))
    if len(words) < 64:
        out.append('    [%d..63] :   0000;' % len(words))
    out.append('END;')
    return '\r\n'.join(out) + '\r\n'

# ------------------------------------------------------------------ reference model
def alu(op, a, b):
    if op == 0: return (a + b) & 15
    if op == 1: return (a - b) & 15
    if op == 2: return (a * b) & 15
    return 15 if b == 0 else a // b

class CPU:
    def __init__(self, rom):
        self.rom = list(rom) + [0] * (64 - len(rom))
        self.reset()
    def reset(self):
        self.r = [0, 0, 0, 0]; self.pc = 0; self.flag = 0
    def step(self):
        w = self.rom[self.pc]
        op, ra, rb, rd = w >> 12, (w >> 10) & 3, (w >> 8) & 3, (w >> 6) & 3
        addr, imm = w & 63, w & 15
        A, B = self.r[ra], self.r[rb]
        nxt = (self.pc + 1) & 63
        if op == 0: self.flag = int(A == B)
        elif op == 1: self.r[rd] = A
        elif op == 2: self.r[rd] = imm
        elif op == 3: self.reset(); return
        elif 4 <= op <= 7: self.r[rd] = alu(op & 3, A, B)
        elif 8 <= op <= 11: self.r[rd] = alu(op & 3, A, imm)
        elif op == 12: nxt = addr
        elif op == 13: nxt = A
        elif op == 14 and A == 0: nxt = addr
        elif op == 15 and self.flag: nxt = addr
        self.pc = nxt

if __name__ == '__main__':
    src = open(sys.argv[1], encoding='utf-8').read()
    words, lines = assemble(src)
    open(sys.argv[2], 'w', newline='').write(to_mif(words, lines))
    print('%d instruções gravadas em %s' % (len(words), sys.argv[2]))
