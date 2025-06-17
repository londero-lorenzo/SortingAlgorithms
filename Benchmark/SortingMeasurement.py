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
    AlgoritmiDiOrdinamento.QuickSort3Way.__name__: lambda array: (array, 0, len(array)),
    AlgoritmiDiOrdinamento.CountingSort.__name__: lambda array: (array, [0]*len(array), max(array)+1),
    AlgoritmiDiOrdinamento.RadixSort.__name__: lambda array: (array, len(str(max(array)+1)))
}



class MeasurableTimeExecutionAlgorithm:
    """
    Wrapper class for managing and executing time-measurable algorithms.
    Allows setting a function from a predefined list, executing it on provided input, and retrieving its name or reference.

    Attributes:
        function (callable): reference to the currently selected algorithmic function.

    Methods:
        set(function: callable) -> None:
            Sets the function to be used, ensuring it is among those defined in AlgorithmArguments.
            Raises an exception if the function is unrecognized.

        get() -> callable:
            Returns the currently set function.

        get_name() -> str:
            Returns the name (string) of the currently set function.

        execute(array: Any) -> Any:
            Executes the selected function on the provided data.
            The actual arguments are dynamically retrieved via `AlgorithmArguments[function_name](array)`.

    Raises:
        Exception: if attempting to set a function not listed in `AlgorithmArguments`.
    """

    # Static attribute: holds the current function (initially None)
    function = None

    def set(self, function):
        """
        Sets the function to be used for measurements.
        Checks that the function name is among the recognized keys in AlgorithmArguments.
        """
        if not function.__name__ in list(AlgorithmArguments.keys()):
            # Raises error if the function is not recognized
            raise Exception(f"Unknown algorithm {function.__name__}.\nAvailable algorithms: {list(AlgorithmArguments.keys())}")

        # Stores the reference to the function to be measured
        self.function = function

    def execute(self, array):
        """
        Executes the currently set function, passing arguments obtained dynamically from AlgorithmArguments.
        """
        # Gets the required arguments for the function based on its name, then executes it
        return self.function(*(AlgorithmArguments[self.get().__name__](array)))

    def get(self):
        """
        Returns the reference to the currently set function.
        """
        return self.function

    def get_name(self):
        """
        Returns the name of the currently set function.
        """
        return self.function.__name__




    
def measure(function: callable, minTime: float, *args) -> float:
    """
    Measures the average execution time of the `function`, repeating it multiple times until
    the total time exceeds `minTime`.

    Args:
        function (callable): the function to be measured. It must accept the arguments provided in `args`.
        minTime (float): minimum cumulative time (in seconds) to reach before calculating the average.
        *args: positional arguments to be passed to the function in each call.

    Returns:
        float: average time (in seconds) for a single execution of the function on `args`.
    """

    count = 0  # Counter for the number of executions performed
    start_time = time.perf_counter()  # High-resolution start time

    while True:
        function(*args)  # Executes the function with the specified arguments
        end_time = time.perf_counter()  # Time after execution
        count += 1  # Increment the number of repetitions

        # If cumulative time exceeds minTime, break the loop
        if end_time - start_time >= minTime:
            break

    # Calculate average time by dividing total time by the number of executions
    return (end_time - start_time) / count


def measure_container_array(array_sample_container: ArrayDataManager.ArraySampleContainer, 
                            function: callable, 
                            minTime: float = None) -> list[ArrayDataManager.ArrayExecutionTime]:
    """
    Measures the execution time of an algorithm (function) on each array contained in an ArraySampleContainer object.

    Args:
        array_sample_container (ArraySampleContainer): container of arrays to measure.
        function (callable of MeasurableTimeExecutionAlgorithm): wrapper of the algorithm to be measured (must be already set).
        minTime (float, optional): minimum cumulative time to measure for each array to obtain a stable average.
            If not specified, it is computed via `SortingSettings.compute_min_time()`.

    Returns:
        List[ArrayExecutionTime]: list of objects representing average execution times for each array configuration.

    Raises:
        AssertionError: if `array_sample_container` is not an instance of `ArraySampleContainer`, or if the container
        structure is altered during measurement.
    """

    # Create two deep copies of the array container to compare structural integrity and operate safely
    array_sample_container_copy_comparison = copy.deepcopy(array_sample_container)
    array_sample_container_copy = copy.deepcopy(array_sample_container)

    # If minTime is not specified, compute it dynamically
    if minTime is None:
        minTime = SortingSettings.compute_min_time()
    
    # Initial quick test to activate potential warm-up optimizations
    [measure(function, minTime, [i for i in range(100)])]

    # Type check: must be an instance of ArraySampleContainer
    assert isinstance(array_sample_container, ArrayDataManager.ArraySampleContainer), \
        f"Chunk element expected as ArraySampleContainer, got {type(array_sample_container)}"
    
    array_execution_times = []  # List of timing results

    # Iterate through each array sample
    for array_sample in array_sample_container_copy.get_samples():
        time_repetitions = []

        # For each repetition of the sample, measure execution time
        for data in array_sample.get_sample():
            time_repetitions.append(measure(function, minTime, data))

        # Build an ArrayExecutionTime object for each sample
        array_execution_times.append(
            ArrayDataManager.ArrayExecutionTime(
                variability = array_sample.get_variability(),
                execution_times = time_repetitions,
                creation_arguments = array_sample.get_creation_arguments()
            )
        )

    # Verify that the initial structure was not modified during measurement
    assert ArrayDataManager.deep_compare(array_sample_container.to_dict(), 
                                         array_sample_container_copy_comparison.to_dict()), \
        f"Modification in array structure detected."
    
    return array_execution_times