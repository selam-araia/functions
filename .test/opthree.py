from exercises import *
import numpy as np


##############
# Sum the array
def check_op_three(asm):

    new_start = """.text
    .global _start
    _start:
  	 movia   sp, 0x04000000
	 #movi r4, 1
     #movi r5, 2   we will set input param
     #movi r6, 3   we will set input param
	 call op_three

	 break


     op_two_add:
       add     r2, r4, r5
       ret


     op_two_mul:
      mul r2, r4, r5
      ret
    
    op_two_xor:
      xor r2, r4, r5
      ret

    op_two:
      # Prologue (save return address)
      subi    sp, sp, 4
      stw     ra, 0(sp)
    

      cmpeqi r10, r7, 0
      movi   r11, 1
    

      beq    r10, r11,  1f 
      br 2f

    1:
      call op_two_add
      br done
      
    
    2:  
      cmpeqi r10, r7, 1
      movi   r11, 1
      beq r10, r11, 3f
      br 4f

    3:
      call op_two_mul
      br done

    4:
      call op_two_xor
      br done

    done:
      # Epilogue (restore return address)
      ldw     ra, 0(sp)
      addi    sp, sp, 4
      ret

    """

    hp = new_start + asm
    obj = nios2_as(hp.encode("utf-8"))
    r = require_symbols(obj, ["_start"])
    if r is not None:
        return (False, r)

    test_cases = [
        ([5, 3, 1 ], 9, 0),  # add
        ([5, 3, 1 ], 15, 1), # mul
        ([5, 3, 1 ], 7, 2) ,  # xor
    ]

    cpu = Nios2(obj=obj)

    feedback = ""
    cur_test = 1
    for arr, ans, op in test_cases:

        # Reset and initialize
        cpu.reset()

        cpu.set_reg(4, np.uint32(np.int32(arr[0])))
        cpu.set_reg(5, np.uint32(np.int32(arr[1])))
        cpu.set_reg(6, np.uint32(np.int32(arr[2])))
        cpu.set_reg(7, np.uint32(np.int32(op)))

        # Run
        instrs = cpu.run_until_halted(10000)
        print("     instrs= %d " % instrs)
        # Check answer
        
        their_ans = cpu.get_reg(2)
        
        if their_ans != ans:
            feedback += "Failed test case %d with op %d: " % (cur_test, op)
            feedback += "Your code produced O=0x%08x" % np.uint32(their_ans)
            #feedback += "DEBUGGING// expcected O=0x%08x" % np.uint32(ans)
            feedback += "<br/><br/>Memory:<br/><pre>"
            feedback += cpu.dump_mem(0, 0x100)
            feedback += "\nSymbols:\n" + cpu.dump_symbols()
            feedback += "</pre>"

            print('Error: %s' % feedback)
            return (False, feedback)


        feedback += "Passed test case %d<br/>\n" % (cur_test)
        cur_test += 1

    print('Passed all tests')


import sys
check_op_three(sys.stdin.read())
