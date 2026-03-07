import os
import sys
from util import nios2_as, get_debug
from csim import Nios2


def check_part2_1(student_input):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'proj3-part2-1.s')) as f:
        asm = f.read()

    obj = nios2_as(asm.encode('utf-8'))
    if not isinstance(obj, dict):
        print('Assembler error: ' + str(obj))
        return

    cpu = Nios2(obj=obj)

    # Feed student input to UART, adding \n if not present
    raw = student_input.rstrip('\n').encode('latin-1') + b'\n'
    input_queue = list(raw)
    output = []

    def uart(val=None):
        if val is None:  # read_chr: ldwio r9, 0(r8)
            if input_queue:
                return 0x8000 | input_queue.pop(0)  # RAVAIL=1 | char
            return 0  # no data available
        else:           # write_chr: stwio r4, 0(r8)
            output.append(val & 0xff)
        return 0

    cpu.add_mmio(0xFF201000, uart)
    cpu.run_until_halted(500000)

    out_str = bytes(output).decode('latin-1')

    if '. Your grade is: A+' in out_str:
        print('Passed')
    else:
        print('Failed')
        print('Output: ' + repr(out_str))


check_part2_1(sys.stdin.read())
