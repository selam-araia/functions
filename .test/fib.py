from util import nios2_as, get_debug, require_symbols, hotpatch, get_regs
from csim import Nios2


start = '''_start:
    # You should probably test your program!
    # Feel free to change the value of N, but leave the rest of
    # this code as is.
    movia   sp, 0x04000000  # Setup the stack pointer
    subi    sp, sp, 4

    movia   r4, N
    ldw     r4, 0(r4)

    call    fib             # fib(N)

    movia   r4, F
    stw     r2, 0(r4)       # store r2 to F
    break                   # r2 should be 55 here.
.data
N:  .word 10
F:  .word 0
'''

############
# Fib
def check_fib(asm):

    hp = asm + start
    obj = nios2_as(hp.encode('utf-8'))
    r = require_symbols(obj, ['N', 'F', '_start', 'fib'])
    if r is not None:
        return (False, r)

    cpu = Nios2(obj=obj)

    tests = [(10, 55), (15, 610), (12, 144), (30, 832040)]
    feedback = ''
    extra_info = ''
    cur_test = 1
    clobbered = set()
    for n,ans in tests:
        cpu.reset()
        cpu.write_symbol_word('N', n)

        instrs = cpu.run_until_halted(100000000)

        # Check for clobbered registers first
        # in case this is why they failed
        clobs = cpu.get_clobbered()
        if len(clobs) > 0:
            for pc,rid,_ in clobs:
                if (pc,rid) not in clobbered:
                    extra_info += 'Warning: Function @0x%08x clobbered r%d\n<br/>' % (pc, rid)
                    clobbered.add((pc, rid))

        # Check answer
        their_ans = cpu.get_symbol_word('F')
        if their_ans != ans:
            feedback += 'Failed test case %d: ' % cur_test
            feedback += 'fib(%d) returned %d, should have returned %d' %\
                    (n, their_ans, ans)
            feedback += get_debug(cpu, show_stack=True)
            del cpu
            return (False, feedback, extra_info)

        feedback += 'Passed test case %d<br/>\n' % cur_test
        cur_test += 1

    del cpu
    return (True, feedback, extra_info)

import sys
passed, feedback, extra_info = check_fib(sys.stdin.read())
if passed:
    print('Passed all tests')
else:
    print('Error:', feedback, extra_info)
