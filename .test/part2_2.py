import os
import re
import sys
from util import nios2_as, get_debug
from csim import Nios2


def parse_ascii(s):
    """Parse the content between quotes in a .ascii directive into bytes."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            if s[i+1] == 'x' and i + 3 < len(s):
                result.append(int(s[i+2:i+4], 16))
                i += 4
            elif s[i+1] == 'n':
                result.append(0x0a)
                i += 2
            elif s[i+1] == '0':
                result.append(0x00)
                i += 2
            elif s[i+1] == '\\':
                result.append(ord('\\'))
                i += 2
            else:
                result.append(ord(s[i+1]))
                i += 2
        else:
            result.append(ord(s[i]))
            i += 1
    return bytes(result)


def check_part2_2(student_data):
    len_match = re.search(r'STUDENT_NAME_LEN:\s*\.word\s+(\S+)', student_data)
    name_match = re.search(r'STUDENT_NAME:\s*\.ascii\s+"([^"]*)"', student_data)

    if not len_match:
        print('Error: could not find STUDENT_NAME_LEN in part2_2.txt')
        return
    if not name_match:
        print('Error: could not find STUDENT_NAME in part2_2.txt')
        return

    try:
        name_len = int(len_match.group(1), 0)
    except ValueError:
        print('Error: invalid STUDENT_NAME_LEN value: ' + len_match.group(1))
        return

    name_bytes = parse_ascii(name_match.group(1))
    name_hex = ''.join(f'\\x{b:02x}' for b in name_bytes)

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'proj3-part2-2.s')) as f:
        asm = f.read()

    # Substitute student's values into the assembly before assembling
    asm = re.sub(r'STUDENT_NAME_LEN:.*',
                 f'STUDENT_NAME_LEN:   .word   {name_len}', asm)
    asm = re.sub(r'STUDENT_NAME:.*\.ascii.*',
                 lambda m: f'STUDENT_NAME:       .ascii "{name_hex}"', asm)

    obj = nios2_as(asm.encode('utf-8'))
    if not isinstance(obj, dict):
        print('Assembler error: ' + str(obj))
        return

    cpu = Nios2(obj=obj)
    output = []

    def uart(val=None):
        if val is None:  # shouldn't be read at 0xFF201000, but handle it
            return 0
        else:            # write_chr: stwio r4, 0(r8)
            output.append(val & 0xff)
        return 0

    def uart_ctrl(val=None):
        if val is None:  # write_chr reads WSPACE from 4(r8) = 0xFF201004
            return 0xFFFF0000  # WSPACE nonzero: always ready to write
        return 0

    cpu.add_mmio(0xFF201000, uart)
    cpu.add_mmio(0xFF201004, uart_ctrl)
    cpu.run_until_halted(500000)

    out_str = bytes(output).decode('latin-1')

    if 'A+!' in out_str:
        print('Passed')
    else:
        print('Failed')
        print('Output: ' + repr(out_str))


check_part2_2(sys.stdin.read())
