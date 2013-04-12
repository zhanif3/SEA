
from Trace       import REIL_Trace
from Inputs      import parse_inputs
from Memory      import MemAccessREIL
from Parameters  import FuncParametersREIL
from Callstack   import CallstackREIL
from Allocation  import Allocation

from Instruction import *
from Reil        import parse_reil
from Operand     import *


def mkTrace(trace_filename, first, last, raw_inputs):
    
    print "Loading trace.."
    reil_code = REIL_Trace(trace_filename, first, last)
    
    Inputs = parse_inputs(raw_inputs)
    
    if (raw_inputs <> []):
      print "Using these inputs.."
    
      for op in Inputs:
        print op,"=", Inputs[op]
    
    print "Detecting callstack layout..."
    Callstack = CallstackREIL(reil_code)#, Inputs) #TODO: it should recieve inputs also!
    
    reil_code.reset()
    
    print Callstack
    
    AllocationLog = Allocation()
    MemAccess = MemAccessREIL()
    FuncParameters = FuncParametersREIL()
    
    reil_size = len(reil_code)
    start = 0  
  
    Callstack.reset()
    
    print "Detecting memory accesses and function parameters.."
  
    for (end,ins_str) in enumerate(reil_code):
      pins = parse_reil(ins_str)
      ins = Instruction(pins,None)
      
      Callstack.nextInstruction(ins_str)
      
      if ins.instruction in ["stm", "ldm"]: 
        MemAccess.detectMemAccess(reil_code[start:end+1], Callstack, Inputs, end)
        AllocationLog.check(MemAccess.getAccess(end), end)
        
      elif ins.instruction == "call" and ins.called_function <> None:
        #print "detect parameters of", ins.called_function, "at", ins_str
        FuncParameters.detectFuncParameters(reil_code[start:end+1], MemAccess, Callstack, Inputs, end)
        if (ins.called_function == "malloc"):
          
          try:
            size = int(FuncParameters.getParameters(end)[0][1].name)
          except ValueError:
            size = None
          AllocationLog.alloc(ins.address, end, size)
        elif (ins.called_function == "free"):
          ptr = (FuncParameters.getParameters(end)[0][1].mem_source)
          AllocationLog.free(ptr, end)
    
    
    print MemAccess
    print FuncParameters
    AllocationLog.report()
    
    
    Callstack.reset()
    reil_code.reset()
    
    # trace definition
    trace = dict()
    trace["code"] = reil_code
    trace["initial_conditions"] = Inputs
    trace["final_conditions"] = dict()
    trace["callstack"] = Callstack
    trace["mem_access"] = MemAccess
    trace["func_parameters"] = FuncParameters
    
    return trace

    
