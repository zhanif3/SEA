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

import SSA

from Instruction import *
from Condition   import *
from SMT         import SMT
from Reil        import parse_reil

def getPathConditions(trace, filename): 

  callstack  = list(trace["callstack"])
  inss       = list(trace["raw_code"])
  mem_access = trace["memaccess"]

  SSA.SSAinit()

  mvars = set()
  smt_conds = SMT() 

  #assert(False)

  for ins_str in inss:
    #print ins_str.strip("\n")
    # Instruction parsing
    pins = parse_reil(ins_str)

    # Instruction processing
    current_call = trace["current_call"]
    mem_access = trace["memaccess"].getAccess(pins.address)
    ins = Instruction(pins,current_call,mem_access)

    ins_write_vars = set(ins.getWriteVarOperands())
    ins_read_vars = set(ins.getReadVarOperands())

    if pins.instruction == "jcc" or len(ins_write_vars.intersection(mvars)) > 0:
      ssa_map = SSA.SSAMapping(ins_read_vars.difference(mvars), ins_write_vars, ins_read_vars.intersection(mvars))

      cons = conds.get(pins.instruction, Condition)
      condition = cons(ins, ssa_map)
     
      mvars = mvars.difference(ins_write_vars) 
      mvars = ins_read_vars.union(mvars)
      mvars = set(filter(lambda o: o.name <> "ebp", mvars))
   
      smt_conds.add(condition.getEq())

    #print "mvars ops:"  
    #for op in mvars:
    #  print op

  smt_conds.write_smtlib_file(filename+".smt2")  
  smt_conds.write_sol_file(filename+".sol") 

