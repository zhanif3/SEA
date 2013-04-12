from pkgs.pyparsing import Word, Literal, alphas, alphanums, delimitedList

address         = Word( alphanums).setResultsName("address")
colon           = Literal( ":" )
instruction     = Word( alphas ).setResultsName("instruction")
left_sbracket   = Literal("[")
right_sbracket  = Literal("]")
operand         = Word( alphanums+"-_" ).setResultsName("operand")
size            = Word( alphas ).setResultsName("size")
no_operand      = Literal( "EMPTY" ).setResultsName("operand") 

aug_operand = (size + operand) | no_operand

comma           = Literal(",")
body            = aug_operand + comma + aug_operand + comma + aug_operand
body            = body.setResultsName("augmented_operands")

reil = address + colon + instruction + left_sbracket + body + right_sbracket

parse_reil = reil.parseString

