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

import sys
sys.path.append("z3py/build/")

import z3

from Instruction import *
from Operand import *
from MemVars import Memvars

def mkArray(name):
  return z3.Array(name, z3.BitVecSort(16), z3.BitVecSort(8))

class Condition:

  def __apply_ssa(self, op):
    if op.isReg():
      return self.ssa_map[str(op)]
    return op

  def __init__(self, ins, ssa_map):
    self.ins = ins
    
    rreg = self.ins.getReadRegOperands()
    wreg = self.ins.getWriteRegOperands()
    
    self.read_operands = self.ins.getReadOperands()
    self.write_operands = self.ins.getWriteOperands()
    
    self.ssa_map = ssa_map    
    self.read_operands = map(lambda o: self.__apply_ssa(o), self.read_operands)
    self.write_operands = map(lambda o: self.__apply_ssa(o), self.write_operands)
  
  def getEq(self):
    return []

  def getOperands(self, ops, concat = True):
   
    rops = [] 
    for op in ops:
      if (op.isVar()):
        if (op.size > 1):
          rops.append(z3.Concat(map(lambda b: z3.BitVec(b,8), op.get_bytes()))) 
        else:
          rops.append(z3.BitVec(op.get_bytes()[0],8))
      else:
          rops.append(z3.BitVecVal(op.getValue(),8*op.size))

    return rops

  def fixOperandSizes(self):
    write_sizes = map(lambda o: o.size, self.write_operands)
    read_sizes = map(lambda o: o.size, self.read_operands)
    
    size = min(min(write_sizes), min(read_sizes))
    assert(size > 0)
    
    for o in self.write_operands:
      o.size = size
   
    for o in self.read_operands:
      o.size = size  

class Call_Cond(Condition):
  def getEq(self):
    return None
 
class  Jcc_Cond(Condition):
  def getEq(self):
    src = self.getOperands(self.read_operands)[0]
    
    if (self.read_operands[-1].name == "0"): # hack to know which branch was taken!
      return [(src == 0)] # False branch
    else: 
      return [(src <> 0)] # True branch
 
class  Str_Cond(Condition):
 def getEq(self):

   src = self.getOperands(self.read_operands)[0]
   dst = self.getOperands(self.write_operands)[0]
   
   return [(src == dst)]

class  Add_Cond(Condition):
 def getEq(self):
   self.fixOperandSizes()

   src1,src2 = self.getOperands(self.read_operands)
   dst = self.getOperands(self.write_operands)[0]
   
   return [(src1 + src2 == dst)]


class  Sub_Cond(Condition):
 def getEq(self):
   
   self.fixOperandSizes()
   src1,src2 = self.getOperands(self.read_operands)
   dst = self.getOperands(self.write_operands)[0]
   
   return [(src1 - src2 == dst)]


class  Mul_Cond(Condition):
 def getEq(self):
   self.fixOperandSizes()
   
   src1,src2 = self.getOperands(self.read_operands)
   dst = self.getOperands(self.write_operands)[0]
   
   return [(src1 * src2 == dst)]

class  And_Cond(Condition):
 def getEq(self):
   
   self.fixOperandSizes()

   src1,src2 = self.getOperands(self.read_operands)
   dst = self.getOperands(self.write_operands)[0]
   
   return [(src1 & src2 == dst)]

class  Or_Cond(Condition):
 def getEq(self):
   
   self.fixOperandSizes()
  
   src1,src2 = self.getOperands(self.read_operands)
   dst = self.getOperands(self.write_operands)[0]
   
   return [(src1 | src2 == dst)]


class  Xor_Cond(Condition):
 def getEq(self):
   
   self.fixOperandSizes()

   src1,src2 = self.getOperands(self.read_operands)
   dst = self.getOperands(self.write_operands)[0]
   
   return [(src1 ^ src2 == dst)]

class  Shift_Cond(Condition):
 def getEq(self):
   
   sdir = ""
   if self.read_operands[1].getValue()>0:
     sdir = "left"
   elif self.read_operands[1].getValue()<0:
     sdir = "right"
     self.read_operands[1].name = self.read_operands[1].name.replace("-","") #ugly hack!
   else:
     sdir = "null"
   
   #print self.read_operands[1].name
   src1,src2 = self.getOperands(self.read_operands)
   dst = self.getOperands(self.write_operands)[0]

   #print sdir, src2.as_long()
   if sdir == "right":   
     return [(z3.Extract(self.write_operands[0].size*8-1, 0,z3.LShR(src1,src2)) == dst)]
   elif sdir == "left":
     return [(z3.Extract(self.write_operands[0].size*8-1, 0,(src1 << src2)) == dst)]
   elif sdir == "null":
     return [(src1 == dst)]
   else:
     assert(False)

class  Bisz_Cond(Condition):
 def getEq(self):
   src = self.getOperands(self.read_operands)[0]
   dst = self.getOperands(self.write_operands)[0]
   
   return [z3.If(src == 0, dst == 1, dst == 0)]

class  Ldm_Cond(Condition):
  def getEq(self):
    sname, offset = Memvars.read(self.ins.getReadMemOperands()[0])
    array = mkArray(sname)
    
    dst = (self.write_operands)[0]
    dsts = map(lambda b: z3.BitVec(b,8), dst.get_bytes())
    dsts.reverse()    

    conds = []
    
    #for (i,dst) in zip(range(offset, offset-(dst.size),-1), dsts):
    for (i,dst) in zip(range(dst.size), dsts):
    #for (i,dst) in zip(range(offset, offset+(dst.size)+1), dsts):
      conds.append(array[offset+i] == dst)

    return conds

class  Stm_Cond(Condition):
  def getEq(self):
    
    src = (self.read_operands)[0]
    if src.isVar():
      srcs = map(lambda b: z3.BitVec(b,8), src.get_bytes())
    else:
      srcs = map(lambda b: z3.BitVecVal(int(b,16),8), src.get_bytes())
      
    srcs.reverse()
    
    conds = []
    offset = Memvars.getOffset(self.write_operands[0])
    old_sname, new_sname, offset = Memvars.write(self.write_operands[0])
      
    old_array = mkArray(old_sname)
    array = mkArray(new_sname)

    #for (i,src) in zip(range(offset,offset-(src.size),-1), srcs):
    #for (i,src) in zip(range(offset,offset+(src.size)+1), srcs):
    for (i,src) in zip(range(src.size), srcs):
      array = z3.Store(array, offset + i, src)
      
    conds = [(old_array == array)]

    return conds


# exploit conditions

class  Write_with_stm(Condition):
  def getEq(self, value, address):
    op_val,op_addr = self.getOperands(self.read_operands)
    print [op_val == value, op_addr == address]
    return [op_val == value, op_addr == address]
  
# generic conditions  
  
class  Eq(Condition):
  def __init__(self, pins, ssa):
    pass
  def getEq(self, x, y):
    
    if x.isMem() and y.isMem():
      src_name, src_offset = Memvars.read(x)
      src_array = mkArray(src_name)
      
      dst_name, dst_offset = Memvars.read(y)
      dst_array = mkArray(dst_name)
      return [src_array[src_offset] == dst_array[dst_offset]]
    
    elif x.isMem() and y.isImm():
      
      assert(y.size == 1) # y should be a BYTE
      
      src_name, src_offset = Memvars.read(x)
      src_array = mkArray(src_name)
      
      dst = self.getOperands([y])
      return [src_array[src_offset] == dst[0]]
    else:
      src, dst = self.getOperands([x,y])
      return [src == dst]  


# Func conditions
class  Call_Gets_Cond(Condition):
  def __init__(self, funcs, ssa):
    self.dst = funcs.parameter_vals[0]
    self.size = funcs.internal_size
  
  def getEq(self, mvars):
    
    r = []

    old_sname, new_sname, offset = Memvars.write(self.dst)
      
    old_array = mkArray(old_sname)
    array = mkArray(new_sname)

    for i in range(self.size):
      
      op = Operand(self.dst.mem_source+"@"+str(offset+i), "BYTE")
      
      if (op in mvars):
        array = z3.Store(array, offset+i, z3.BitVec("stdin:"+str(i)+"(0)",8))
        
      r.append(z3.BitVec("stdin:"+str(i)+"(0)",8) <> 10)
      r.append(z3.BitVec("stdin:"+str(i)+"(0)",8) <> 0)
      
    r.append((old_array == array))

    return r


class  Call_Strlen_Cond(Condition):
  def __init__(self, funcs, ssa):
  
  
    self.ssa_map = ssa_map    
    self.read_operands = map(lambda o: self.__apply_ssa(o), self.read_operands)
    self.write_operands = map(lambda o: self.__apply_ssa(o), self.write_operands)
    
    self.src    = self.read_operands[0]
    self.retreg = self.write_operands[0]
    self.size = funcs.internal_size
    
  
  def getEq(self, mvars):
    
    retreg = self.getOperands([self.retreg])
    return retreg == self.size
  
class  Call_Strcpy_Cond(Condition):
  def __init__(self, funcs, ssa):
    self.src = funcs.parameter_vals[1]
    self.dst = funcs.parameter_vals[0]
    self.size = funcs.internal_size
  
  def getEq(self, mvars):
    
    r = []
    
    #print self.src, self.dst
    
    if (self.src.isReg()):
      src = self.src.name
    #  self.src.size = self.size
    #  srcs = self.getOperands([self.src])
    #  print srcs
    else:
      assert(0)
  
    old_sname, new_sname, offset = Memvars.write(self.dst)
      
    old_array = mkArray(old_sname)
    array = mkArray(new_sname)
    
    for i in range(self.size):
      
      dst_op = Operand(self.dst.mem_source+"@"+str(offset+i), "BYTE")
      src_var = z3.BitVec(src+":"+str(i)+"(0)",8)
      
      if (dst_op in mvars):
        array = z3.Store(array, offset+i, src_var)

      r.append(src_var <> 0)
      
    r.append((old_array == array))

    return r


conds = {
    "call" : Call_Cond,
    
    "gets" : Call_Gets_Cond,
    "strcpy" : Call_Strcpy_Cond,
    
    "jcc": Jcc_Cond,
    "str": Str_Cond,
    "and": And_Cond,
    "or": Or_Cond,
    "xor": Xor_Cond,
    "bsh": Shift_Cond,
    "add": Add_Cond,
    "sub": Sub_Cond,
    "mul": Mul_Cond,
    "bisz": Bisz_Cond,
    
    "ldm": Ldm_Cond,
    "stm": Stm_Cond,
    }
