import z3
import copy

class AST(object):
    def __init__(self, d):
        self.data = d
        self.child = []

    def add_child(self, t):
        self.child.append(t)

    def __repr__(self):
        return '{d}:{c}'.format(d = self.data, c = self.child)

    def createAST(self, code):
        i = 0
        while i < len(code):
            if code[i] != '(':
                print "syntax error"
                sys.exit(-1)
            codeblock = ""
            nest = 0
            while True:
                codeblock += code[i]
                i += 1
                if code[i-1] == ')':
                    nest -= 1
                    if nest == 0:
                        break
                elif code[i-1] == '(':
                    nest += 1
            name = ""
            j = 1
            while codeblock[j] != '(' and codeblock[j] != ')':
                name += codeblock[j]
                j += 1
            t = AST(name)
            t.createAST(codeblock[j:-1])
            self.child.append(t)
                

def parse(ast, memory, memidx):
    output = []
    for i in ast.child:
        if i.data == "inp":
            memory[memidx] = int(raw_input("Enter input: "))
        elif i.data == "out":
            output.append(memory[memidx])
        elif i.data == "add":
            memory[memidx] += 1
        elif i.data == "sub":
            memory[memidx] -= 1
        elif i.data == "movl":
            memidx -= 1
        elif i.data == "movr":
            memidx += 1
        elif i.data == "while":
            while memory[memidx] != 0:
                (memory, memidx, x) = parse(i, memory, memidx)
                if x:
                    output.append(x)
        else:
            print "Invalid code type"
            return []
        
    return (memory, memidx, output)

class TerminateState(Exception):
    pass

class State(object):
    def __init__(self, ast, astiter, memory, memidx, inp, out, path, maxnest):
        self.memory = memory
        self.memidx = memidx
        self.out = out
        self.inp = inp
        self.ast = ast
        self.path = path
        self.astiter = astiter
        self.sat = False
        self.model = None
        self.maxnest = maxnest

    def concretize(self):
        s = z3.Solver()
        s.add (z3.simplify(z3.And(*self.path)))
        if s.check() == z3.unsat:
            return False
        self.sat = True
        self.model = s.model()
        return True

    def clone(self):
        #############################################################################
        # TODO: work with copy & assignment properly for not wasting much of memory #
        #############################################################################
        return State(self.ast, copy.deepcopy(self.astiter), copy.copy(self.memory), self.memidx, copy.copy(self.inp), copy.copy(self.out), copy.copy(self.path), self.maxnest)

    def nextstate(self):
        if self.ast.data == "seq":
            (a, b, _) = self.astiter[0]
            if a >= len(b.child):
                raise TerminateState()

        (astiter, ast, t) = self.astiter.pop()
        if ast.data == "while" and astiter >= len(ast.child):
            (astiter, ast, t_new) = self.astiter.pop()
        currnode = ast.child[astiter]
        #st = copy.copy(self) # deepcopy won't work :/ make own copy function
        if currnode.data == "add":
            st = self.clone()
            st.memory[st.memidx] += 1#z3.simplify(st.memory[st.memidx] + 1)
            st.astiter.append((astiter + 1, ast, t))
            return [st]
        elif currnode.data == "sub":
            st = self.clone()
            st.memory[st.memidx] -= 1#z3.simplify(st.memory[st.memidx] - 1)
            st.astiter.append((astiter + 1, ast, t))
            return [st]
        elif currnode.data == "movl":
            st = self.clone()
            st.memidx -= 1
            st.astiter.append((astiter + 1, ast, t))
            return [st]
        elif currnode.data == "movr":
            st = self.clone()
            st.memidx += 1
            st.astiter.append((astiter + 1, ast, t))
            return [st]
        elif currnode.data == "inp":
            st = self.clone()
            inp = (z3.Int("inp_{}".format(len(self.inp))))
            st.memory[st.memidx] = inp
            st.inp.append(inp)
            st.astiter.append((astiter + 1, ast, t))
            return [st]
        elif currnode.data == "out":
            st = self.clone()
            st.out.append(st.memory[st.memidx])
            st.astiter.append((astiter + 1, ast, t))
            return [st]
        elif currnode.data == "while":
            st = self.clone()
            if self.memory[self.memidx] == 0:
                st.astiter.append((astiter + 1, ast, t))
                return [st]
            noloop = st            
            noloop.path.append(noloop.memory[noloop.memidx] == 0)
            noloop.memory[noloop.memidx] = 0
            noloop.astiter.append((astiter + 1, ast, t))
            retstate = [noloop]
            if not (self.memory[self.memidx] == 0):
                if self.maxnest < 0 or 1 ==1 :
                    inloop = self.clone()
                    inloop.path.append(inloop.memory[inloop.memidx] != 0)
                    inloop.astiter.append((astiter, ast ,t))
                    inloop.astiter.append((0, currnode, t))
                    retstate.append(inloop)
            return retstate
        else:
            print "WTF? undefined code"
            return []


class PathGroup(object):
    def __init__(self, live, dead):
        self.live = live
        self.dead = dead
        self.goal = set()

    def execute_pathgroup_till_goal(self, goalfunction):
        while self.live:
            st = self.live.pop()
            if goalfunction(st):
                self.goal.add(st)
                return ## Use this return if you want to stop at single solution
            try:
                nextst = st.nextstate()
                #print ">>>> {} ..... {} ..... {}".format(st.path, st.memory[0:5], st.astiter)
                #for a in nextst:
                #    print ">> {} ..... {} ..... {}".format(a.path, a.memory[0:5], a.astiter)
                self.live.update(set(nextst))
            except TerminateState:
                self.dead.add(st)
            print "{} live, {} dead, {} goal".format(len(self.live),
                                                     len(self.dead),
                                                     len(self.goal))

        return
