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

from Operand     import *
from Condition   import *

def getInitialConditionsCall(callstack):
  
  initial_values_at_call = dict()
  
  if callstack.index == 1:
    
    esp_val = 4
    
    for i in range(0,40):
      arg_i = Operand("argv[]@"+str(i),"BYTE", mem_source = "argv[]", mem_offset=i)
      initial_values_at_call[arg_i] = Operand(str(0), "BYTE")
    
    name = "s."+hex(callstack.callstack[1])+".1"
  
    for i in range(12,16):
      arg_v = Operand(name+"@"+str(i),"BYTE", mem_source = name, mem_offset=i)
      initial_values_at_call[arg_v] = Operand(str(0), "BYTE")
    
    #print ""
  else:
    esp_val = 8
 
  ebp_val = 0
  
  esp_op = Operand("esp","DWORD")
  ebp_op = Operand("ebp","DWORD")
  
  
  initial_values_at_call[esp_op] = Operand(str(esp_val), "DWORD")
  initial_values_at_call[ebp_op] = Operand(str(ebp_val), "DWORD")
  
  return initial_values_at_call

def getInitialConditionsAlloc():
  ret_op = Operand("eax","DWORD")
  ret_val = 0
  initial_values_at_alloc = dict()
  initial_values_at_alloc[ret_op] = Operand(str(ret_val), "DWORD")
  
  return initial_values_at_alloc

def setInitialConditions(ssa, initial_values, smt_conds):
  ssa_map = ssa.getMap(set(), set(), set(initial_values.keys()))
  eq = Eq(None, None)
  
  for iop in initial_values:
    
    if ":" in iop.name:
      smt_conds.add(eq.getEq(iop,initial_values[iop]))
    elif (iop.isReg()):
      smt_conds.add(eq.getEq(ssa_map[iop.name],initial_values[iop]))
    elif (iop.isMem()):
      smt_conds.add(eq.getEq(iop,initial_values[iop]))
    else:
      assert(False)

def detectType(mvars, ins, counter, callstack):
  
  if (len(mvars) == 0):
    return None
  
  # dection of parameters of main
  
  name = "s."+hex(callstack.callstack[1])+".1"
  
  # argv
  argv_bytes = []
  
  for i in range(12,16):
    argv_bytes.append(Operand(name+"@"+str(i),"BYTE"))
  
  argv_bytes = set(argv_bytes) 
  
  
  if argv_bytes.issubset(mvars):
    return "argv[]"
  
  ## argc
  #argc_bytes = []
  #
  #for i in range(8,12):
  #  argc_bytes.append(Operand(name+"@"+str(i),"BYTE"))
  #
  #argc_bytes = set(argv_bytes) 
  #
  #if argc_bytes.issubset(mvars):
  #  return "argc"
  
  # argv[0], argv[1], ... argv[10]
  for i in range(0,40,4):
    op = Operand("argv[]@"+str(i),"BYTE")
    if op in mvars:
      return "arg["+str(i / 4)+"]"
  
  if ins.instruction == "call" and ins.called_function == "malloc":
    
    # heap pointers
    if set([Operand("eax","DWORD")]).issubset(mvars):
      return "h."+"0x"+ins.address+"."+str(counter)
  
  elif ins.instruction == "call" and ins.called_function == None:
    
    # stack pointers
    if mvars.issubset(set([Operand("esp", "DWORD"), Operand("ebp", "DWORD")])):
      return "s."+hex(callstack.currentCall())+"."+str(callstack.currentCounter())

  # No type deduced
  return None 

def mkVal(val_type,val):
  if val_type == "imm":
    return Operand(str(val), "")
  elif "s." in val_type or "h." in val_type or "arg" in val_type:
    return Operand(val_type+"@"+str(val), "", mem_source = val_type, mem_offset=val)
  else:
    assert(0)
    
def addAditionalConditions(mvars, ins, ssa, callstack, smt_conds):
  
  if len(mvars) == 0:
    return mvars
  
  # auxiliary eq condition
  eq = Eq(None, None)
  
  # if the instruction was a call
  if ins.instruction == "call" and ins.called_function == "malloc":

    if (Operand("eax","DWORD") in mvars):
      initial_values_at_alloc = getInitialConditionsAlloc()
      setInitialConditions(ssa, initial_values_at_alloc, smt_conds)
      mvars.remove(Operand("eax","DWORD"))
      
  elif ins.instruction == "call" and ins.called_function == None:
    initial_values_at_call = getInitialConditionsCall(callstack)
      
    
    for iop in initial_values_at_call.keys():
      #print "iop:",iop
      if not (iop in mvars):  
        del initial_values_at_call[iop]
      
      
    setInitialConditions(ssa, initial_values_at_call, smt_conds)
    mvars = set(filter(lambda o: not (o in initial_values_at_call.keys()), mvars))
    
      
    new_mvars = set()
    for v in mvars:
      # we convert stack memory variables from one frame to the previous one
      if callstack.currentCounter()>1 and v.isStackMem() and v.mem_offset >= 4: 
        eop = callstack.convertStackMemOp(v)
        smt_conds.add(eq.getEq(v,eop))
        new_mvars.add(eop)
      else:
        new_mvars.add(v)
      
    mvars = set(filter(lambda o: not (o.isStackMem() and o.mem_offset >= 4), mvars))
    mvars = mvars.union(new_mvars)
  
  return mvars
  
