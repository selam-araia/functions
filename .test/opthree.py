from util import nios2_as, get_debug, require_symbols
from csim import Nios2
import numpy as np
import ctypes


def check_project3_1_2(asm):

    new_start = """.text
    .global _start
    _start:
        movia   sp, 0x03fffffc
        call    op_three
        break

    op_two:
        movia   r15, 0x13371000
        stwio   r4, 0(r15)      # write a
        stwio   r5, 4(r15)      # write b (triggers computation, stores result)

        # trash caller-saved registers to test ABI compliance
        movui   r4, 0xdead
        movui   r5, 0xbeef
        movui   r6, 0xcafe
        movui   r7, 0xbabe
        movui   r8, 0x1111
        movui   r9, 0x2222
        movui   r10, 0x3333
        movui   r11, 0x4444
        movui   r12, 0x5555
        movui   r13, 0x6666
        movui   r14, 0x7777

        ldwio   r2, 4(r15)      # read result

        ret
    """

    hp = new_start + asm
    obj = nios2_as(hp.encode("utf-8"))
    r = require_symbols(obj, ["op_three", "_start"])
    if r is not None:
        print(r)
        return

    def bits2int(n):
        return ctypes.c_int32(n).value

    def int2bits(n):
        return ctypes.c_uint32(n).value

    class OpTwo:
        def __init__(self, fn):
            self.fn = fn
            self.a = 0
            self.result = 0

        def set_a(self, val=None):
            if val is not None:
                self.a = bits2int(val)
            return self.result

        def compute(self, val=None):
            if val is not None:
                b = bits2int(val)
                self.result = int2bits(self.fn(self.a, b))
            return self.result


    test_cases = [
        ([5, 3, 1], 'add', lambda a, b: a + b, 9),
        ([5, 3, 1], 'mul', lambda a, b: a * b, 15),
        ([5, 3, 1], 'xor', lambda a, b: a ^ b, 7),
        ([-1, 1, 1], 'add', lambda a, b: a + b, 1),
        ([-10, 4, -3], 'add', lambda a, b: a + b, -9),
        ([2, 3, 4], 'mul', lambda a, b: a * b, 24),
    ]

    cpu = Nios2(obj=obj)

    for i, (arr, op_name, op_fn, expected) in enumerate(test_cases):
        op = OpTwo(op_fn)
        cpu.reset()
        cpu.add_mmio(0x13371000, op.set_a)
        cpu.add_mmio(0x13371004, op.compute)

        cpu.set_reg(4, np.uint32(np.int32(arr[0])))
        cpu.set_reg(5, np.uint32(np.int32(arr[1])))
        cpu.set_reg(6, np.uint32(np.int32(arr[2])))

        cpu.run_until_halted(100)

        their_ans = np.int32(np.uint32(cpu.get_reg(2)))

        for addr, rid, _ in cpu.get_clobbered():
            print('Warning: function @0x%08x clobbered r%d' % (addr, rid))

        if their_ans != np.int32(expected):
            print('Failed test %d (op=%s, args=%s): got %d, expected %d' %
                  (i + 1, op_name, arr, their_ans, expected))
            print(get_debug(cpu, show_stack=True))
            del cpu
            return

    del cpu
    print('Passed all tests')


import sys
check_project3_1_2(sys.stdin.read())
