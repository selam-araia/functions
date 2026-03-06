from util import nios2_as, get_debug, require_symbols, hotpatch, get_regs
from csim import Nios2
import numpy as np

##############
# Project 3 
def check_project3_1_1(asm):

    new_start = """.text
    .globl _start
      _start:
        movia   sp, 0x03fffffc
	    call sum_two 
	    break
      """
    hp = new_start + asm
    obj = nios2_as(hp.encode("utf-8"))
    r = require_symbols(obj, ["sum_two"])
    if r is not None:
        return (False, r)

    test_cases = [
        ([5, 3], 8),  # add
        ([15, -3 ], 12), 
        ([995, 10], 1005), 
        ([-10,-25], -35),
    ]

    cpu = Nios2(obj=obj)

    feedback = ""
    cur_test = 1
    for arr, ans in test_cases:

        # Reset and initialize
        cpu.reset()

        cpu.set_reg(4, np.uint32(np.int32(arr[0])))
        cpu.set_reg(5, np.uint32(np.int32(arr[1])))

        # Run
        instrs = cpu.run_until_halted(1000)
        #print("     instrs= %d " % instrs)
        # Check answer
        
        their_ans = np.int32(np.uint32(cpu.get_reg(2)))
        
        if their_ans != np.int32(ans):
            feedback += "Failed test case %d " % cur_test
            feedback += "Your code produced O=0x%08x" % their_ans
            feedback += "<br/><br/>Memory:<br/><pre>"
            feedback += cpu.dump_mem(0, 0x100)
            feedback += "\nSymbols:\n" + cpu.dump_symbols()
            feedback += "</pre>"

            print('Failed test %d: %s' % (cur_test, feedback))
            return


        #feedback += "Passed test case %d<br/>\n" % (cur_test)
        cur_test += 1


    print('Passed all tests')

import sys
check_project3_1_1(sys.stdin.read())
