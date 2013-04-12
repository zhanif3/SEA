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

from Instruction import *
from Reil        import parse_reil
from Operand     import *
from Function    import *
from Common      import getTypedValueFromCode

class FuncParametersREIL:
  def __init__(self):
    self.parameters = dict()
    
  def __str__(self):
    
    counters = self.parameters.keys()
    counters.sort()
    
    ret = "Parameters detected:"
    
    for c in counters:
      ret = ret + "\n" + str(c) + " -> "
      param_info = self.parameters[c]
      fname = param_info["function"]
      ret = ret + fname + "("
      
      for (l,p) in param_info["parameters"]:
        #print self.parameters[c]#["function"]
        ret = ret  + " " +  str(l) + " := " + str(p) + ","
      ret = ret + ")"
    
    return ret
  
  def getParameters(self, counter):
    
    if counter in self.parameters:
      return self.parameters[counter]["parameters"]
    
    return None
    
  def detectFuncParameters(self, reil_code, memaccess, callstack, inputs, counter):
    
    pins = parse_reil(reil_code[-1])
    ins = Instruction(pins,None)
    
    assert(ins.instruction == "call" and ins.called_function <> None)
    
    # first we locate the stack pointer to know where the parameters are located
    esp = Operand("esp","DWORD")
    pbase = getTypedValueFromCode(reil_code, callstack, inputs, memaccess, esp)
    
    #print pbase.name
    #print pbase.mem_source
    #
    func_cons = funcs.get(ins.called_function, Function)
    func = func_cons(pbase = pbase)
    
    parameters = []
    
    for (par_type, location, needed) in func.getParameterLocations():
      #print (ins.called_function, par_type, location.mem_source, needed)
      if needed:
        reil_code.reverse()
        reil_code.reset()
        val = getTypedValueFromCode(reil_code, callstack, inputs, memaccess, location)
        #print  "parameter of",ins.called_function, "at", str(location) , "has value:", val.name
        parameters.append((location, val))
      else:
        parameters.append((None, None))
    
    if parameters <> []:
      self.parameters[counter] = self.__getParameters__(ins, parameters)
    

  def __getParameters__(self, ins, raw_parameters):
    parameters = dict()
    parameters["function"] = ins.called_function
    parameters["parameters"] = list(raw_parameters)
    parameters["address"]   = ins.address
    
    return parameters
