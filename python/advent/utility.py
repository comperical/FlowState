
import os
import sys
from collections import deque



def read_input_deque(pcode):
    indq = deque([])
    inputpath = os.path.join(get_data_dir(), '{}.txt'.format(pcode))

    with open(inputpath, 'r') as fh:
        for line in fh:
            indq.append(line.strip())

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
    probes = ["p{:02}".format(idx) for idx in range(1, 25)]
    assert argstr in probes, "Invalid problem code {}, format is pXY".format(argstr)
    return argstr