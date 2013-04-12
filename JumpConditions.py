
from Reil        import parse_reil
from Common      import getPathConditions

from Instruction import *

input_vars = ["stdin:", "arg[0]@0:", "arg[1]@0:", "arg[2]@0:"]

def getJumpConditions(trace, addr):
  raw_ins = parse_reil(trace["code"][-1])
  addr = int(addr, 16)
  pos = trace["code"].last - 1
  
  if (raw_ins.instruction == "jcc"):
    ins = Instruction(raw_ins, None)
    jmp_op = ins.operands[2]
    
    if (jmp_op.isVar()):
      
      #print addr  
      trace["final_conditions"] = dict([( jmp_op , Operand(str(addr), "DWORD"))])
      sol = getPathConditions(trace)
      
      if (sol <> None):
        print "SAT conditions found!"
        filename = raw_ins.instruction + "[" + str(pos)  +"]"
        dumped = sol.dump(filename,input_vars)
        for filename in dumped:
          print filename, "dumped!"
      else:
        print "Impossible to jump to", hex(addr), "from", raw_ins.instruction, "at", pos
    else:
      return None
    
  else:
    return None