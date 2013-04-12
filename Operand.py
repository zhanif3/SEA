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

import copy, math

def detectType(x):
  if x == "EMPTY":
    return ""
  
  if "s." in x:
    return "smem"
  
  if "g." in x:
    return "gmem"
  
  if "h." in x:
    return "hmem"
  
  if "argv" in x:
    return "hmem"
  
  try:
    y = int(x)
    return "imm"
  except ValueError:
    return "reg"
  
size_in_bytes = {
    "BYTE": 1,
    "WORD": 2,
    "DWORD": 4,
    "QWORD": 8,
}

class Operand:

  def __init__(self, name, size, mem_source = None, mem_offset = None):
    self.type = detectType(name)
    
    # for memory operand
    self.mem_source = None
    self.mem_offset = None
    
    if (mem_source <> None and mem_offset <> None):
      self.mem_source = mem_source
      self.mem_offset = mem_offset
    
    self.name = name
    self.size = size_in_bytes.get(size, 0)

    #assert(not ((self.size <> 0) and (self.name <> "EMPTY")) or) 
    #assert((self.size == 0) and (self.name == "EMPTY")) 

  def copy(self):
    return copy.copy(self)
   
  def __str__(self):
    return self.name

  def __cmp__(self, op):
    return cmp(self.name,op.name)
  
  def __hash__(self):
    return hash(self.name)

  def isEmpty(self):
    return self.type == ""

  def isReg(self):
    return self.type == "reg"
  
  def isVar(self):
    return self.type in ["reg", "smem", "gmem", "hmem"]
  
  def isImm(self):
    return self.type == "imm"
  
  def isMem(self):
    return self.type in ["smem", "gmem", "hmem"]
  
  def isStackMem(self):
    return self.type in ["smem"]
  
  def isHeapMem(self):
    return self.type in ["hmem"]

  def get_bytes(self):
    assert(self.size <> 0)
    r = []

    if (self.type == "reg"):
      for i in range(self.size):
        r.append(self.name+"("+str(i)+")")
    elif (self.type == "mem"):
      r = [self.name]
    else:
      fmt = "%016x"
      hx = (fmt % int(self.name))
      for i in range(0,16,2):
        r.append("0x"+hx[i:i+2])
      r.reverse() #??
      r = r[0:self.size]

    # handle endianess
    r.reverse() # little endian

    return r   
  
  def getValue(self):
    return int(self.name)
