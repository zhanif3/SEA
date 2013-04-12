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

from SSA import SSA

from Instruction import *
from Condition   import *
from SMT         import SMT
from Reil        import parse_reil
from Operand     import *

def getValueFromCode(inss, initial_values, op):
  assert(len(inss) > 0)
  
  # code should be copied and reversed
  inss.reverse()
  
  # counter is set
  counter = len(inss)
  
  ssa = SSA()
  smt_conds  = SMT()
 
  # we will track op
  mvars = set([op])    
  ssa.getMap(mvars, set(), set())

  for ins_str in inss:
    #print ins_str.strip("\n")
    pins = parse_reil(ins_str)
      
    ins = Instruction(pins, None) # no memory and callstack are available
    
    ins_write_vars = set(ins.getWriteVarOperands())
    ins_read_vars = set(ins.getReadVarOperands())

    if len(ins_write_vars.intersection(mvars)) > 0: 
      
      ssa_map = ssa.getMap(ins_read_vars.difference(mvars), ins_write_vars, ins_read_vars.intersection(mvars))

      cons = conds.get(pins.instruction, Condition)
      condition = cons(ins, ssa_map)
     
      mvars = mvars.difference(ins_write_vars) 
      mvars = ins_read_vars.union(mvars)
      mvars = set(filter(lambda o: o.name <> "ebp", mvars))
   
      smt_conds.add(condition.getEq())
      
    counter = counter - 1
  
  for iop in initial_values.keys():
    if not (iop in ssa):
      del initial_values[iop]
    
  ssa_map = ssa.getMap(set(), set(), set(initial_values.keys()))
  eq = Eq(None, None)
    
  for iop in initial_values:
    smt_conds.add(eq.getEq(ssa_map[iop.name],initial_values[iop]))
  
  op.name = op.name+"_0"
  smt_conds.solve()
  
  return smt_conds.getValue(op)


class CallstackREIL:
  def __init__(self, reil_code):
    
    # The first instruction should be a call
    self.callstack = [None]
    self.stack_diff = []
    
    self.index = 0
    #self.prev_callstack = [None]
    
    # aditional information need to compute the callstack
    self.calls = [None]
    self.esp_diffs = [None]
    self.reil_code = reil_code
    reil_size = len(reil_code)
    start = 0  
  
    for (end,ins_str) in enumerate(self.reil_code):
      #print ins_str.strip("\n")
      pins = parse_reil(ins_str)
      ins = Instruction(pins, None)
  
      if (ins.instruction == "call" and ins.called_function == None) or ins.instruction == "ret":
        self.__getStackDiff__(ins.instruction, ins.address,reil_code[start:end])
        start = end
        
    if (start <> reil_size-1):
      pins = parse_reil(reil_code[start])
      self.__getStackDiff__(pins.instruction, pins.address,reil_code[start:reil_size])
      
    self.index = len(self.callstack) - 1
  
  def __str__(self):
    ret = ""
    #for addr in reversed(self.prev_callstack):
    #  if (addr <> None):
    #    ret = ret + " " + hex(addr)
    
    #ret = ret + "->"
    #print len(self.callstack), len(self.stack_diff)
    for (addr, sdiff) in zip(self.callstack, self.stack_diff):
      if (addr <> None):
        ret = ret + " " + hex(addr) + "[" +str(sdiff)+"]"
    
    return ret
  
  def reset(self):
    self.index = 0
  
  def nextInstruction(self, ins):
    pins = parse_reil(ins)
    if pins.instruction == "call" or pins.instruction == "ret":
      self.index = self.index + 1
  
  
  def prevInstruction(self, ins):
    pins = parse_reil(ins)
    if pins.instruction == "call" or pins.instruction == "ret":
      self.index = self.index - 1
  
  def currentCall(self):
    return self.callstack[self.index]
    
  def currentStackDiff(self):
    return self.stack_diff[self.index]
  
  def currentCounter(self):
    return 1 # TODO!
  
  def firstCall(self):
    return self.index == 1
  
  def convertStackMemOp(self, op):
    
    #print str(op)
    
    self.index = self.index - 1
    
    mem_source =  "s."+hex(self.currentCall())+"."+str(self.currentCounter())
    if self.index == 1:
      mem_offset = (op.mem_offset)+self.currentStackDiff()-4#+16
    else:
      mem_offset = (op.mem_offset)+self.currentStackDiff()#+16
    name = mem_source+"@"+str(mem_offset)
    
    self.index = self.index + 1
    
    return Operand(name,"BYTE", mem_source, mem_offset)
  
  def __getStackDiff__(self, inst, addr,reil_code):
    if inst == "call":
      call = int(addr, 16)
      esp_diff = self.__getESPdifference__(reil_code, 0) 
        
      self.calls.append(call)
      self.callstack.append(call)
        
      self.stack_diff.append(esp_diff)
      self.esp_diffs.append(esp_diff)
      
    elif inst == "ret":
        
      if (parse_reil(reil_code[0]).instruction == "call"):
        self.stack_diff.append(self.__getESPdifference__(reil_code, 0))
      else:
        self.calls.pop()
        self.esp_diffs.pop()
          
        call = self.calls[-1]
        esp_diff = self.esp_diffs[-1]
          
        self.stack_diff.append(self.__getESPdifference__(reil_code, esp_diff)) 
        self.callstack.append(call)
    else:
      assert(False)
  
  def __getESPdifference__(self, reil_code, initial_esp):
    #print "inf:", reil_code.first, reil_code.last
    if len(reil_code) == 0:
      return initial_esp
    
    esp_op = Operand("esp","DWORD")
    initial_values = dict([ (esp_op, Operand(str(0), "DWORD"))])
    return getValueFromCode(reil_code, initial_values, esp_op)+ initial_esp
