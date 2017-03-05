import sys
import parsecode

"""
BF:

There are eight commands:
+ : Increments the value at the current cell by one.
- : Decrements the value at the current cell by one.
> : Moves the data pointer to the next cell (cell on the right).
< : Moves the data pointer to the previous cell (cell on the left).
. : Prints the ASCII value at the current cell (i.e. 65 = 'A').
, : Reads a single input character into the current cell.
[ : If the value at the current cell is zero, skips to the corresponding ] .
    Otherwise, move to the next instruction.
] : If the value at the current cell is zero, move to the next instruction.
    Otherwise, move backwards in the instructions to the corresponding [ .

[ and ] form a while loop. Obviously, they must be balanced.


Equivalent Language:

(while statement1 statement2 . . . . .)
(add)
(sub)
(movl)
(movr)
(inp)
(out)
"""

def convertcode(code):
    retcode = ""
    for i in code:
        if i == '+':
            retcode += "(add)"
        elif i == '-':
            retcode += "(sub)"
        elif i == '<':
            retcode += "(movl)"
        elif i == '>':
            retcode += "(movr)"
        elif i == ',':
            retcode += "(inp)"
        elif i == '.':
            retcode += "(out)"
        elif i == '[':
            retcode += "(while"
        elif i == ']':
            retcode += ")"
        else:
            print i
            print "This should not have been reached"
    return retcode

def cleanup_code(code):
    retcode = ""
    for i in code:
        if i in ['<','>','+','-',',','.','[',']']:
            retcode += i

    return retcode

def usage():
    print """
    Usage:
    	<executable> <bf_code_filename>
    """

if __name__ == "__main__":
    """
    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    with open(sys.argv[1]) as fp:
        code = fp.read()
    """

    #code = ">+[>,[>+<-]] <[<] >>[.>]"
    #code = ",>,[<+>-]<."
    code = ",[[>+>+<<-]>[<+>-]<-]>>."
    #code = ",>,<[>[>+>+<<-]>>[-<<+>>]<<<-]>>."
    #code = ",."
    code = convertcode (cleanup_code(code))

    print code
    ast = parsecode.AST("seq")
    ast.createAST(code)
    print ast

    memory = [0 for i in range(1000)]
    memidx = 0
    output = []
    #(memory, memidx, output) = parsecode.parse(ast, memory, memidx)
    #print memidx, output

    memory = [0 for i in range(1000)]
    inp = []
    output = []
    path = []
    astiter = [(0, ast, 0)]

    initialstate = parsecode.State(ast, astiter, memory, 0, inp, output, path, 3)
    live = {initialstate}
    dead = set()
    pg = parsecode.PathGroup(live, dead)
    def goal_fn(st):
        if len(st.astiter) != 1:
            return False
        (a, b, _) = st.astiter[0]
        if a != len(b.child):
            return False
        st.path.append(st.inp[0] > 0)
        #st.path.append(st.inp[1] )
        st.path.append(st.out[0] == 6)
        if st.concretize():
            return True
        return False
    
    pg.execute_pathgroup_till_goal(goalfunction = goal_fn)
    for s in pg.goal:
        print s.model
        print s.out
        print s.path
