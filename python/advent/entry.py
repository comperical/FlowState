
import sys
import importlib

import utility as U

sys.path.append("../")


if __name__ == "__main__":
        
    assert len(sys.argv) >= 3, "Usage entry.py <solve|diagram|run2step|test> pXY ..."
    assert sys.argv[1] in ['solve', 'diagram', 'run2step', 'test']

    pcode = U.check_problem_code(sys.argv[2])
    pmod = importlib.import_module(pcode)

    pmachine = pmod.PMachine()

    if sys.argv[1] == 'diagram':
        print("Going to make diagram")
        U.create_diagram(pmachine, pcode)
        quit()
    
    if sys.argv[1] == 'solve':
        pmachine.run2_completion()
        print("Result is : {}".format(pmachine.get_result()))

    if sys.argv[1] == 'run2step':
        stepcount = int(sys.argv[3])
        print("Running machine to step {}".format(stepcount))
        pmachine.run2_step_count(stepcount)

    if sys.argv[1] == 'test':
        pmod.run_tests()