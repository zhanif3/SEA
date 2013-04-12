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

from Operand import *

class SSA:
  def __init__(self):
    self.regs = dict()
    
  def __contains__(self, op):
    return str(op) in self.regs
  
  def getMap(self, read_ops, write_ops, other_ops):
    d = dict()
    
    read_ops  = filter(lambda o: not o.isMem(), read_ops)
    write_ops = filter(lambda o: not o.isMem(), write_ops)
    other_ops = filter(lambda o: not o.isMem(), other_ops)

    #print self.regs

    for op in read_ops:
      d[str(op)] = self.renameReadOperand(op)

    for op in write_ops:
      d[str(op)] = self.renameWriteOperand(op)

    for op in other_ops:
      if (str(op) in self.regs):
        d[str(op)] = self.renameWriteOperand(op)
      else:
        op_ren = op.copy()
        op_ren.name = op_ren.name+"_0"
        d[str(op)] = op_ren
        

    #print regs
    #print d
  
    return d
  
  def renameReadOperand(self, op):
  
    #if not op.is_reg:
    #  return op.copy()  
  
    if not (str(op) in self.regs):
      self.regs[str(op)] = -1
  
    self.regs[str(op)] = self.regs[str(op)] + 1
    op_ren = op.copy()
    op_ren.name = str(op)+"_"+str(self.regs[str(op)]) 

    return op_ren


  def renameWriteOperand(self, op):
  
    #if not op.is_reg:
    #  return op.copy()    
  
    op_ren = op.copy()
    op_ren.name = str(op)+"_"+str(self.regs[str(op)]) 

    return op_ren
