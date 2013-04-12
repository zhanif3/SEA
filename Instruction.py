from Operand import *

class Instruction:
  """An abstract instruction class"""
  def __init__(self, pins, mem_access, mem_regs = True):
    self.address = pins.address
    self.instruction = pins.instruction
    #print pins.instruction, mem_access
    self.operands = []
    
    # for memory instructions
    self.mem_reg = None
    
    # for call instructions
    self.called_function = None
    
    aopers = pins.augmented_operands
    for (i,x) in enumerate(aopers):
       if x == ",":
        self.operands.append(Operand(aopers[i-1], aopers[i-2]))
    self.operands.append(Operand(aopers[-1], aopers[-2]))
    
    self.read_operands = []
    self.write_operands = []
    
    # ldm: op_2 = [op_0]
    if (pins.instruction == "ldm"):
      
      self.write_operands = [self.operands[2]]
      self.mem_reg = self.operands[0]
      
      if (mem_access <> None):
        
        #if (mem_regs):
        #  self.read_operands  = [self.operands[0]]
        
        mem_source = mem_access["source"]
        mem_offset = mem_access["offset"]
        for i in range(self.operands[2].size):
          name = mem_source+"@"+str(mem_offset+i)
          self.read_operands.append(Operand(name, "BYTE", mem_source, mem_offset+i))
         
        #self.read_operands.append(self.operands[0])
      #else:
      #  print "#WARNING: No memory access information of ldm in", self.address
      
    # stm: [op_2] = op_0
    elif (pins.instruction == "stm"):
      
      self.read_operands.append(self.operands[0])
      self.mem_reg = self.operands[2]
      
      if (mem_access <> None):
      #  if (mem_regs):
      #    self.write_operands = [self.operands[2]]
        
        mem_source = mem_access["source"]
        mem_offset = mem_access["offset"]
        for i in range(self.operands[0].size):
          name = mem_source+"@"+str(mem_offset+i)
          self.write_operands.append(Operand(name, "BYTE", mem_source, mem_offset+i))
      #else:
      #  print "#WARNING: No memory access information of stm in", self.address
      
    elif (pins.instruction == "jcc"):
      self.read_operands  = filter(lambda o: not o.isEmpty(), self.operands[0:2])
      self.write_operands = []
      
    elif (pins.instruction == "call"):
      #print self.operands[0].name
      if (self.operands[0].name <> "EMPTY"):
        self.called_function = self.operands[0].name
      
    else:
      
      self.read_operands  = filter(lambda o: not o.isEmpty(), self.operands[0:2])
      self.write_operands = filter(lambda o: not o.isEmpty(), self.operands[2:3])
      
    

  def getOperands(self):
#   if (pins.instruction == "ldm"):
#     return list(self.read_operands[1:] + self.write_operands) 
#   if (pins.instruction == "stm"):
#     return list(self.read_operands[1:] + self.write_operands) 
#   else:
    return list(self.read_operands + self.write_operands)
  
  def getReadOperands(self):
    return list(self.read_operands)

  def getWriteOperands(self):
    return list(self.write_operands)

  def getReadRegOperands(self):
    return filter(lambda o: o.isReg(), self.read_operands)

  def getWriteRegOperands(self):
    return filter(lambda o: o.isReg(), self.write_operands)
  
  def getReadVarOperands(self):
    return filter(lambda o: o.isVar(), self.read_operands)

  def getWriteVarOperands(self):
    return filter(lambda o: o.isVar(), self.write_operands)
  
  def getReadMemOperands(self):
    return filter(lambda o: o.isMem(), self.read_operands)

  def getWriteMemOperands(self):
    return filter(lambda o: o.isMem(), self.write_operands)
  
  def getMemReg(self):
    return self.mem_reg 

  #def getEq(self):
  #  return  None


