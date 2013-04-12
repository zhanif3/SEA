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
