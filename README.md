### Description

"Symbolic Exploit Assistant" ( **SEA** ) is a small tool designed to assist the discovery and construction of exploits in binary programs. This tool is developed in colaboration between the research institutes [CIFASIS](http://www.cifasis-conicet.gov.ar/) (Rosario, Argentina) and [VERIMAG](http://www-verimag.imag.fr) (Grenoble, France) in an effort to improve security in binary programs.

### Quick Start

To get started, you should have **Python 2.7**. To prepare the tool, the official Z3 Python binding ([z3py](http://research.microsoft.com/en-us/um/redmond/projects/z3/)) should be installed. Fortunately, just executing **boostrap.sh** will download and compile z3py.

After it finishes compiling, SEA is ready to be used. You can test SEA analyzing the converted code of the [first example](http://community.corest.com/~gera/InsecureProgramming/stack1.html) of Gera's Insecure Programming:

    ./SEA.py tests/reil/stack1_gcc.reil
    
The **complete analysis** of this example can be found [here](https://github.com/neuromancer/SEA/wiki/Warming-up-on-stack---1).

### There is always a catch..

**NOTE**: Right now, SEA uses REIL code as input, to analyze a path. Unfortunately, REIL can be **only** generated from an executable file using [BinNavi](http://www.zynamics.com/binnavi.html) which runs in the top of [IDA-Pro](https://www.hex-rays.com/products/ida/index.shtml) (two proprietary and expensive programs)
Hopefully, this will change soon when SEA supports open frameworks for binary analysis like Bincoa or BAP.

Documentation, examples and more can be found in the [wiki](https://github.com/neuromancer/SEA/wiki). Collaboration and feedback is greatly appreciated!.
