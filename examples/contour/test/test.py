import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
sieve_root = os.path.dirname(os.path.dirname(os.path.dirname(current)))
sys.path.append(sieve_root)

from sieve_test_driver.test_framework import new_built_in_workload

test_cases = {
    "create": new_built_in_workload(50)
    .cmd("kubectl apply -f examples/contour/test/gateway.yaml")
    .cmd("kubectl apply -f examples/contour/test/kuard.yaml")
}

test_cases[sys.argv[1]].run(sys.argv[2])
