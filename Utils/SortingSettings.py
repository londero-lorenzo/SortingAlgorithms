import time
import os
from Utils.ArraySettings import VARIABILITY

EXECUTION_TIMES_FOLDER = os.sep.join(["Benchmark", "ExecutionTimes", f"{VARIABILITY.value['code']}_variability"])
EXECUTION_TIMES_GRAPH_FOLDER = os.sep.join(["Report", "Charts", f"{VARIABILITY.value['code']}_variability"])
EXECUTION_TIMES_FILE_EXTENSION = ".time"

RELATIVE_TIME_ERROR = 0.001

def clock_resolution():
    """
    Compute system clock resolution
    """
    start = time.perf_counter()
    
    while start == time.perf_counter():
        pass
    
    stop = time.perf_counter()
    return stop - start

def get_time_resolution(iterations = 500):
    """
    Compute a mean of system clock resolution over iterations 
    """
    return sum([clock_resolution() for _ in range(iterations)])/iterations



def compute_min_time(iterations= 500):
    """
    Compute minimum measurable time based on a RELATIVE_TIME_ERROR
    """
    return get_time_resolution(iterations)*(1/RELATIVE_TIME_ERROR + 1)
