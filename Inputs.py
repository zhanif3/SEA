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