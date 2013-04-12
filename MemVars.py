
class MemVars:

  def __init__(self):
    self.sources = dict()
    
  def reset(self):
    self.sources = dict()

  def createSource(self, src):
    
    if not (src in self.sources):
      self.sources[src] = 0
    else:
      self.sources[src] += 1

  def write(self, mem_op):

    sname = mem_op.mem_source
    offset = mem_op.mem_offset

    if not sname in self.sources:
      self.createSource(sname)

    old_sname = sname + "_" +str(self.sources[sname])
    self.createSource(sname)
    
    new_sname = sname + "_" +str(self.sources[sname])
    return (old_sname, new_sname, offset)

  def read(self, mem_op):
    sname = mem_op.mem_source
    offset = mem_op.mem_offset

    if not sname in self.sources:
      self.createSource(sname)
    
    sname = sname + "_" +str(self.sources[sname])
    return sname, offset
  
  def getOffset(self, mem_op):
    return mem_op.mem_offset
  
Memvars = MemVars()