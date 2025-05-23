import time
import os
from Utils.ArraySettings import VARIABILITY

EXECUTION_TIMES_FOLDER = os.sep.join(["Benchmark", "ExecutionTimes", f"{VARIABILITY.value['code']}_variability"])
EXECUTION_TIMES_GRAPH_FOLDER = os.sep.join(["Report", "Charts", f"{VARIABILITY.value['code']}_variability"])
EXECUTION_TIMES_FILE_EXTENSION = ".time"

def getTimeResolution(iterations = 500):

    samples = []
    for i in range(iterations):
        start = time.perf_counter()
        while time.perf_counter() == start:
            pass
        stop = time.perf_counter()
        samples.append(stop - start)
    
    return sum(samples)/iterations


RELATIVE_TIME_ERROR = 0.001

def compute_min_time(iterations= 500):
    return getTimeResolution(iterations)*(1/RELATIVE_TIME_ERROR + 1)
