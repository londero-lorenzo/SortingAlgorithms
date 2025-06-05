import AlgoritmiDiOrdinamento
import time
import numpy as np
import copy

#### --- MAKING ROOT PROJECT FOLDER VISIBLE AT SCRIPT LEVEL ---

##
## --- Finding root project folder ---
##     (needed to import settings)
##
import os, sys
projectRoot = ""

for folderPathIndex in range(len(os.getcwd().split(os.sep))-1):
    projectRoot = os.sep.join(os.getcwd().split(os.sep)[:-folderPathIndex-1])
    if not os.path.exists(os.sep.join([projectRoot, "ROOT_BEACON"])):
        projectRoot = ""
    else:
        break

assert projectRoot != "", "Unable to find project root.\nNo 'ROOT_BEACON' file found at project root level!"


## --- Adding root porject folder to current system path ---
if projectRoot not in sys.path:
    sys.path.insert(1, projectRoot)
    
####                    --- end ---

from Utils import ArraySettings
from Utils import ArrayDataManager
from Utils import SortingSettings
sys.setrecursionlimit(ArraySettings.MAXIMUM_ARRAY_LENGTH+1)

# lambda dict to calculate arguments for each sorting algorithm 
AlgorithmArguments = {
    AlgoritmiDiOrdinamento.InsertionSort.__name__: lambda array: (array, ),
    AlgoritmiDiOrdinamento.QuickSort.__name__: lambda array: (array, 0, len(array)-1),
    AlgoritmiDiOrdinamento.QuickSort3Way.__name__: lambda array: (array, 0, len(array)-1),
    AlgoritmiDiOrdinamento.CountingSort.__name__: lambda array: (array, [0]*len(array), max(array)+1),
    AlgoritmiDiOrdinamento.RadixSort.__name__: lambda array: (array, len(str(max(array)+1)))
}




##
##   ----------    DEFINITIONS FOR MULTIPROCESSING    ----------
##


#class used in multiprocessing runtime
class MeasurableTimeExecutionAlgorithm:

    function = None

    def set(self, function):
        if not function.__name__ in list(AlgorithmArguments.keys()):
            raise Exception(f"Unknown algorithm {function.__name__}.\nAvaliable algorithms: {list(AlgorithmArguments.keys())}")

        self.function = function
        
    def execute(self, array):
        return self.function(*(AlgorithmArguments[self.get().__name__](array)))

    def get(self):
        return self.function

    def get_name(self):
        return self.function.__name__
    
## function to measure sorting time for single array
def measure(function, minTime, *args):
    count = 0
    start_time = time.perf_counter()
    while True:
        function(*args)
        end_time = time.perf_counter()
        count += 1
        if end_time - start_time >= minTime:
            break
    return (end_time - start_time) / count

    
## function to measure sorting time for determinate array chunk
def measure_container_array(array_sample_container, function, minTime= None):
    array_sample_container_copy_comparison = copy.deepcopy(array_sample_container)
    array_sample_container_copy = copy.deepcopy(array_sample_container)

    if minTime is None:
        minTime = SortingSettings.compute_min_time()
    
    [measure(function, minTime, [i for i in range(100)])]
    assert isinstance(array_sample_container, ArrayDataManager.ArraySampleContainer), f"Chunk element expected as ArraySampleContainer, got {type(array_sample_container)}"
        
    array_execution_times = []
    for array_sample in array_sample_container_copy.get_samples():
        time_repetitions= []
        
        for data in array_sample.get_sample():
            time_repetitions.append(measure(function, minTime, data))
                 
        array_execution_times.append(
            ArrayDataManager.ArrayExecutionTime(
                variability = array_sample.get_variability(),
                execution_times = time_repetitions,
                creation_arguments = array_sample.get_creation_arguments()
            )
        )
    
    assert ArrayDataManager.deep_compare(array_sample_container.to_dict(), array_sample_container_copy_comparison.to_dict()), f"Modification in array structure detected."
    return array_execution_times

    