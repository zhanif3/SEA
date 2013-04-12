"""
    This file is part of SEA.

    reserbot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    reserbot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SEA.  If not, see <http://www.gnu.org/licenses/>.

    Copyright 2013 by neuromancer
"""

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
