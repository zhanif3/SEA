from Operand import *

class Function:
  """An abstract function class"""
  parameter_typs = []
  parameter_locs = []
  parameter_vals = []
  read_operands  = []
  write_operands = []
  return_type    = None
  
  def __init__(self, pins = None, pbase = None):
    self.parameter_typs = []
    self.parameter_locs = []
    self.parameter_vals = []
    self.read_operands  = []
    self.write_operands = []
  
  def getParameters(self):
    return self.parameter_vals

  def getParameterLocations(self):
    return self.parameter_locs
  
  def getReadVarOperands(self):
    return filter(lambda o: o.isVar(), self.read_operands)
  
  def getWriteVarOperands(self):
    return filter(lambda o: o.isVar(), self.write_operands)
  
  def getEq(self):
    return []
  
  def __loadParameters__(self, pars):
    self.parameter_locs = []
    self.parameter_vals = []
    
    for (loc, val) in pars:
      self.parameter_locs.append(loc)
      self.parameter_vals.append(val)
    
  
  def __locateParameter__(self, disp, size):
    
    #assert(disp<=0)
    
    mem_source = self.pbase.mem_source
    mem_offset = self.pbase.mem_offset + disp
    name = mem_source + "@" + str(mem_offset)
    return Operand(name, size, mem_source, mem_offset)
  
class Skip_Func(Function):
  pass

class Gets_Func(Function):
  parameter_typs = [("char * str", "DWORD", 0, True)]
  return_type    = "void"
  
  def __init__(self, pbase = None, pars = None):
    
    self.internal_size = 84
    
    if (type(pbase) <> type(None)):
      self.pbase = pbase
      for (ptype, size, disp, needed) in self.parameter_typs:
        self.parameter_locs.append((ptype, self.__locateParameter__(disp, size), needed))
    else:
      self.__loadParameters__(pars)
      
      # populate read operands
      
      self.read_operands.append(self.parameter_locs[0])
      
      # it is not necesary, since these locations won't be modified!
      #for i in range(self.internal_size):
      #  self.read_operands.append(Operand("stdin:"+str(i), "BYTE"))
        
      # populate write operands
      
      for i in range(self.internal_size):
        mem_source = self.parameter_vals[0].mem_source
        mem_offset = self.parameter_vals[0].mem_offset + i
        name = mem_source + "@" + str(mem_offset)
        self.write_operands.append(Operand(name, "BYTE", mem_source, mem_offset))
        
      #print len(self.write_operands)


class Strlen_Func(Function):
  parameter_typs = [("char * str", "DWORD", 0, True)]
  return_type    = "int"
  
  def __init__(self, pbase = None, pars = None):
    
    self.internal_size = 10
    
    if (type(pbase) <> type(None)):
      self.pbase = pbase
      for (ptype, size, disp, needed) in self.parameter_typs:
        self.parameter_locs.append((ptype, self.__locateParameter__(disp, size), needed))
    else:
      self.__loadParameters__(pars)
      
      # populate read operands
      
      self.read_operands.append(self.parameter_locs[0])
        
      # return value
      self.write_operands.append(Operand("eax", "DWORD"))  


      
class Strcpy_Func(Function):
  parameter_typs = [("char * str", "DWORD", 0, True), ("char * str", "DWORD", 4, True)]
  return_type    = "void"
  
  def __init__(self, pbase = None, pars = None):
    
    self.internal_size = 256+4
    
    if (type(pbase) <> type(None)):
      self.pbase = pbase
      for (ptype, size, disp, needed) in self.parameter_typs:
        self.parameter_locs.append((ptype, self.__locateParameter__(disp, size), needed))
    else:
      self.__loadParameters__(pars)
      
      # populate read operands
      
      self.read_operands.append(self.parameter_locs[0])
      self.read_operands.append(self.parameter_locs[1])
      
      for i in range(self.internal_size):
        msrc = self.parameter_vals[1].mem_source
        if ("arg[" in msrc): #it's an argument!
          self.read_operands.append(Operand(msrc+":"+str(i), "BYTE"))
        else:
          assert(0)
        #self.read_operands.append(Operand("i:"+str(i), "BYTE"))
        
      # populate write operands
      
      for i in range(self.internal_size):
        mem_source = self.parameter_vals[0].mem_source
        mem_offset = self.parameter_vals[0].mem_offset + i
        name = mem_source + "@" + str(mem_offset)
        self.write_operands.append(Operand(name, "BYTE", mem_source, mem_offset))

class Alloc_Func(Function):
  parameter_typs = [("int", "DWORD", 0, True)]
  return_type    = "void *"
  
  def __init__(self, pbase = None, pars = None):
    
    self.parameter_locs = []
    self.parameter_vals = []
    self.read_operands  = []
    self.write_operands = []
    
    if (type(pbase) <> type(None)):
      self.pbase = pbase
      for (ptype, size, disp, needed) in self.parameter_typs:
        self.parameter_locs.append((ptype, self.__locateParameter__(disp, size), needed))
    else:
      self.__loadParameters__(pars)

class Free_Func(Function):
  parameter_typs = [("void *", "DWORD", 0, True)]
  return_type    = "void"
  
  def __init__(self, pbase = None, pars = None):
    
    self.parameter_locs = []
    self.parameter_vals = []
    self.read_operands  = []
    self.write_operands = []
    
    if (type(pbase) <> type(None)):
      self.pbase = pbase
      for (ptype, size, disp, needed) in self.parameter_typs:
        self.parameter_locs.append((ptype, self.__locateParameter__(disp, size), needed))
    else:
      self.__loadParameters__(pars)
      

funcs = {
    "printf" : Skip_Func,
    "puts"   : Skip_Func,
    "gets"   : Gets_Func,
    "malloc" : Alloc_Func,
    "free"   : Free_Func,
    "strcpy" : Strcpy_Func,
    "strlen" : Strlen_Func,
}
