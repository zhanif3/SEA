#!/usr/bin/python2

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

import sys
import argparse

from Prelude            import mkTrace
from Common             import getPathConditions
from JumpConditions     import getJumpConditions

parser = argparse.ArgumentParser(description='Symbolic Exploit Assistant.')
parser.add_argument('trace_filename', metavar='trace', type=str,
                    help='a sequence of REIL instruction in a trace')

parser.add_argument('-first', dest='first', action='store', type=int,
                   default=0, help='first instruction to process')

parser.add_argument('-last', dest='last', action='store', type=int,
                   default=sys.maxint-1, help='last instruction to process')

parser.add_argument('-type', dest='type', action='store', type=str,
                   default="debug", help='exploit type')

parser.add_argument('-address', dest='address', action='store', type=str,
                   default=None, help='which address to jump in jump mode')

parser.add_argument('iconditions', metavar='operator,value', type=str, nargs='*',
                   help='initial conditions for the trace')

args = parser.parse_args()

mode  = args.type

if not (mode in ["jump", "path", "debug"]):
  print "\""+mode+"\" is an invalid type of operation for SEA"
  exit(1)

address = args.address
trace = mkTrace(args.trace_filename, args.first, args.last, args.iconditions)

if (mode == "jump"):
  if (address == None):
    print "An address to jump to should be specified!"
  else:
    getJumpConditions(trace, address)

elif (mode == 'path'): 
  
  # TODO: move to PathConditions.py?
  sol = getPathConditions(trace)
  if (sol <> None):
    print "SAT conditions found!"
    input_vars = ["stdin:", "arg[0]@0:", "arg[1]@0:", "arg[2]@0:"]
    pos = trace["code"].last - 1
    
    filename = "path." + "[" + str(pos)  +"]"
    
    dumped = sol.dump(filename,input_vars)
    for filename in dumped:
      print filename, "dumped."
    
elif (mode == 'debug'):
  pass
