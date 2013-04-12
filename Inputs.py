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

from Condition   import *
from Operand     import *

def parse_inputs(inputs):
  
  r = dict()  
    
  for s in inputs:
    #print s
    s = s.strip("(").strip(")")
    (rop, rval) = s.split(",")
    ropsize, rop  = rop.split(" ")
    rvalsize, rval = rval.split(" ")
    
    mem_source = None
    mem_offset = None
    
    
    
    if ('arg[' in rop):
      pass  
    
    elif ('@' in rop):
      mem_source, mem_offset = rop.split('@')
      mem_offset = int(mem_offset)
    
    
    if (ropsize == rvalsize and rvalsize == "VAR"):
      for i,c in enumerate(rval):
        # TODO: this is only for inputs!
        r[Operand(rop+str(i), "BYTE", mem_source, mem_offset)] =  Operand(str(ord(c)), "BYTE")
    else:
      r[Operand(rop, ropsize, mem_source, mem_offset)] =  Operand(rval, rvalsize)
  
  return r
