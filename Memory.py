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

from Instruction import *
from Reil        import parse_reil
from Operand     import *
from Common      import getTypedValueFromCode
  
class MemAccess:
  def getAccess(self, addr):
    pass  

class MemAccessREIL(MemAccess):
  def __init__(self):
    self.access = dict()
  
  def __str__(self):
    
    counters = self.access.keys()
    counters.sort()
    
    ret = "Memory accesses detected:\n"
    
    for c in counters:
      ret = ret + str(c) + " -> " + str(self.access[c]["type"]) + " : " 
      ret = ret + str(self.access[c]["source"]) + "@" + str(self.access[c]["offset"]) + "\n"
    
    return ret
  
  def getAccess(self, counter):
    
    if counter in self.access:
      return self.access[counter]
    
    return None

  def detectMemAccess(self, reil_code, callstack, inputs, counter):
    
    pins = parse_reil(reil_code[-1])
    ins = Instruction(pins,None)
  
    assert(ins.instruction in ["stm", "ldm"])
    addr_op = ins.getMemReg()
    #print "op:", addr_op, ins.address
    val = getTypedValueFromCode(reil_code, callstack, inputs, self, addr_op)
    #print val
    if (val.isMem()):
      
      #if self.__isArgMem__(val, callstack.callstack[1]):
      #  print "arg detected at", ins, "with", str(val)
      #  self.access[counter] = self.__getArgMemAccess__(ins, val, callstack.callstack[1])
      #else:
      #print val
      self.access[counter] = self.__getMemAccess__(ins, val)
    elif (val.isImm):
      self.access[counter] = self.__getGlobalMemAccess__(ins, int(val.name))
    
    else:
      assert(0)
      
  #def __isArgMem__(self, val, main_addr):
  #  return ("s."+hex(main_addr) in val.name and val.mem_offset >= 8)
  #    
  #def __getArgMemAccess__(self, ins, val, main_addr):
  #  mem_access = dict()
  #  mem_access["source"] = "a."+hex(main_addr)+"." + str(int((val.mem_offset-4) / 4)-1) # FIXME: it's a hack!
  #  mem_access["offset"] = (val.mem_offset - 4) % 4 
  #  mem_access["type"]   = ins.instruction
  #  mem_access["address"]   = ins.address
  #  
  #  return mem_access

  def __getMemAccess__(self, ins, val):

    mem_access = dict()
    mem_access["source"] = val.mem_source
    mem_access["offset"] = val.mem_offset
    mem_access["type"]   = ins.instruction
    mem_access["address"]   = ins.address
    
    return mem_access
      
  def __getGlobalMemAccess__(self, ins, offset):
    mem_access = dict()
    mem_access["source"] = "g.0x00000000.0"
    mem_access["offset"] = offset
    mem_access["type"]   = ins.instruction
    mem_access["address"]   = ins.address
    
    return mem_access

