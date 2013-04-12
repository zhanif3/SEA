
class Allocation:
  buffers  = dict()
  dfrees   = []
  overflows= [] 
  uaf      = []
  
  def __init__(self):
    self.buffers = dict()
    
  def alloc(self, address, counter, size):
    self.buffers["h.0x"+str(address)+"."+str(counter)] = size
    
  def free(self, buf, counter):
    if (buf in self.buffers):
      del self.buffers[buf]
    else:
      self.dfrees.append((buf, counter))
      
  def check(self, memaccess, counter):
    
    mem_source = memaccess["source"]
    mem_offset = memaccess["offset"]
    
    if ("h." in mem_source):
      if (not (mem_source in self.buffers.keys())):
        self.uaf.append((mem_source, counter))
      else:
        size = self.buffers[mem_source]
        
        if (mem_offset >= size):
          self.overflows.append((mem_source, mem_offset, counter))
  
  def report(self):
    
    if (len(self.buffers) > 0):
      print "Live buffers:"
      print self.buffers
    else: 
      print "No live buffers."
      
    if (self.overflows <> []):
      print "Heap overflow detected!"
      for (s,o,c) in self.overflows:
        print s, "("+str(o)+")", "at", c 

    if (self.uaf <> []):
      print "Use-after-free detected!"
      for (s,c) in self.uaf:
        print s, "at", c
        
    if (self.dfrees <> []):
      print "Double frees detected!"
      for (s,c) in self.dfrees:
        print s, "at", c
      
    
    
#AllocationLog = Allocation()