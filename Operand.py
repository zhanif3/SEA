"""
   Copyright (c) 2013 galapago
   All rights reserved.
   
   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:
   1. Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
   3. The name of the author may not be used to endorse or promote products
      derived from this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
   IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
   OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
   IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
   NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
   THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
