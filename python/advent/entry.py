
import sys
import importlib

import utility as U

sys.path.append("../")


if __name__ == "__main__":
        
    assert len(sys.argv) >= 3, "Usage entry.py <solve|diagram> pXY ..."
    assert sys.argv[1] in ['solve', 'diagram']

    pcode = U.check_problem_code(sys.argv[2])
    pmod = importlib.import_module(pcode)

    pmachine = pmod.PMachine([5,4,3,2,1])

    if sys.argv[1] == 'diagram':
        print("Going to make diagram")
        U.create_diagram(pmachine, pcode)
        quit()
    
    if sys.argv[1] == 'solve':
        pmachine.run2_completion()
        print("Result is : {}".format(pmachine.get_result()))