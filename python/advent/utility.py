
import os
import sys
from collections import deque


def extract_path(state, parents):

    prnt = parents[state]

    if prnt == None:
        return [state]

    return extract_path(prnt, parents) + [state]


def state_search(start, succfunc, goalfunc, breadth=True):
    
    parents = { }

    stack = deque( [(start, None)] )

    goal = None

    while goal == None and stack:

        nstate, prnt = stack.popleft() if breadth else stack.pop()

        if nstate in parents:
            #Already explored, move on to next
            continue

        # Log visitation of new state
        parents[nstate] = prnt

        if goalfunc(nstate):
            # Success, will end loop in next go-around
            goal = nstate

        # Extend the stack with all the ORDERED successors of the state
        successors = [(succ, nstate) for succ in succfunc(nstate)]
        if not breadth:
            successors = reversed(successors)

        stack.extend(successors)
        #stack.extend([(succ, nstate) for succ in succfunc(nstate)])

    #for state, prnt in stack:
    #    print("State ={}".format(state))


    return goal, parents



def read_input_deque(pcode, dostrip=True):
    indq = deque([])
    inputpath = os.path.join(get_data_dir(), '{}.txt'.format(pcode))

    with open(inputpath, 'r') as fh:
        for line in fh:
            line = line.strip() if dostrip else line
            indq.append(line)

    return indq


def create_diagram(pmachine, pcode, keepgv=False):
    gvpath = get_diagram_path(pcode, 'gv')
    pngpath = get_diagram_path(pcode, 'png')
    graphlabel = "Machine_{}".format(pcode)
    write_gv_output(pmachine.get_gv_tool(graphlabel=graphlabel), gvpath)

    dotcall = "dot {} -Tpng > {}".format(gvpath, pngpath)
    print(dotcall)
    os.system(dotcall)

    if not keepgv:
        os.remove(gvpath)

    return pngpath

def get_data_dir():
    basepath = os.path.dirname(__file__)
    return os.path.join(basepath, 'data')

def get_diagram_path(pcode, extend):
    assert extend in ['gv', 'png']

    basepath = __file__
    for _ in range(3):
        basepath = os.path.dirname(basepath)

    return os.path.join(basepath, 'diagram', 'advent', '{}.{}'.format(pcode, extend))


def write_gv_output(gvtool, gvpath):
    print("Writing to path: {}".format(gvpath))

    with open(gvpath, 'w') as fh:
        for line in gvtool.get_gv_line_output():
            fh.write(line+"\n")

    print("Wrote GV output to path {}".format(gvpath))



def check_problem_code(argstr):

    for idx in range(1, 25):
        for charcode in ['a', 'b', 'c']:
            if argstr == "p{:02}{}".format(idx, charcode):
                return argstr

    assert False, "Invalid problem code {}, format is pXY[a|b|c]".format(argstr)