import os
import numpy as np
import traceback
import multiprocessing as mp
from multiprocessing import Lock
import psutil
import time
import threading
from .MultiprocessingSettings import MULTIPROCESSING_POOL_GUARD_FILE, SAFE_PROCESS_COUNT, FULL_THROTTLE_PROCESS_COUNT
from .MinHeap import MinHeap

#print(f"[Process PID {os.getpid()}] Job {job_index} started."
def partial_callback(function, index):
    return lambda res: function(index, res)
# this function is global, so pickleable
# non-process and thread safe
def default_process_function(_args):
    function, job_index, args, kwargs, high_priority = _args
    try:
        job_label = f"[Process PID {os.getpid()}] Job {job_index} started"
        if high_priority:
            p = psutil.Process(os.getpid())
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            job_label += " with high priority"
        job_label += "."
        print(job_label)
        result = function(*args, **kwargs)
        print(f"[Process PID {os.getpid()}] Job {job_index} completed.")
        return job_index, result
    except Exception as e:
        print(f"[Process PID {os.getpid()}] Job {job_index} crashed: {traceback.format_exc()}")
        return job_index, e # important step: in this way error_callback will be triggered


class OrderedCallbacks:
    def __init__(self, initial_data= None):
        self._heap = MinHeap()
        self._next_order = 0
        self._lock = threading.Lock() 
        self.callback = None
        self.error_callback = None

    def set(self, callback, error_callback):
        self.callback = callback
        self.error_callback = error_callback

    def execute(self, job_index, job_result):
        with self._lock:
            print(f"[Info] Receiving callback from job {job_index}.")
            assert isinstance(job_index, int), f"Job index is expected as int, got {type(job_index)}"
            self._heap.insert(MinHeap.Node(job_index, job_result))
            print(f"[Info] Callback execution added to queue...")
            while self._heap.peek() is not None and self._heap.peek().key == self._next_order:
                sorted_job_indext, sorted_job_result = self._heap.pop().data
                if isinstance(sorted_job_result, Exception):
                    self._error_callback(sorted_job_indext, sorted_job_result)
                else:
                    self._callback(sorted_job_indext, sorted_job_result)
                self._heap.validate_heap()
                self._next_order += 1

    def _callback(self, iterator_index, iterator_result):
        print(f"[Info] Callback for job {iterator_index} running in thread: {threading.current_thread().name}")
        if self.callback is None:
            print(f"[Info] Callback terminated: Job {iterator_index} completed.")
            return None
        try:
            self.callback(iterator_index, iterator_result)
            print(f"[Info] Callback terminated: Job {iterator_index} completed.")
        except Exception as e:
            print(f"[ERROR] Callback for process {iterator_index} failed: {e}")
            traceback.print_exc()

    def _error_callback(self, iterator_index, iterator_error):
        print(f"[ERROR] Process {iterator_index} raised an error: {iterator_error}")
        if self.error_callback is None:
            return
        try:
            self.error_callback(iterator_index, iterator_error)
        except Exception as e:
            print(f"[ERROR] Error callback for process {iterator_index} failed: {e}")
            traceback.print_exc()


    def reset(self):
        self._heap.clear()
        self._next_order = 0


## class used to create a pool of workers that operates simultaneously
class MultiProcessing:

    class JobParameters:
        def __init__(self, args, kwargs, function= None, high_priority= False):
            self.function= function
            self.args = args
            self.kwargs = kwargs
            self.high_priority = high_priority
    
        def get_function(self):
            return self.function
    
        def get_args(self):
            return self.args
    
        def get_kwargs(self):
            return self.kwargs

        def has_high_priority(self):
            return self.high_priority
    
        def copy(self):
            return MultiProcessing.JobParameters(function= self.get_function(), args= self.get_args(), kwargs= self.get_kwargs(), high_priority= self.high_priority)
    
        def get_all_args(self):
            return self.get_args(), self.get_kwargs()


    
    
    @staticmethod
    def create_job_arguments(*args, **kwargs):
        return MultiProcessing.JobParameters(args= args, kwargs= kwargs)

    def __init__(self, project_root_path= None):
        self.results = []
        self.project_root_path = project_root_path
        if not self.project_root_path:
            print("[Warning] No project root set. Unable to check whether other processes are running at project level.")
            self.project_root_path = os.path.dirname(os.path.abspath(__file__))
        print("[Info] Guard file will be generated in: {}".format(self.project_root_path))
        self.guard_file_path = os.sep.join([self.project_root_path, MULTIPROCESSING_POOL_GUARD_FILE])
        self.ordered_callbacks = OrderedCallbacks()

    ### main function that handle the created workers.
    ## Input:
    ##   - iterator: list; the wolkers are spawn from iteration of this list
    ##   - function: lambda, function; a task that every worker has to solve
    ##   - function_arguments: lambda, function; the arguments of the task
    ##   - callback: lambda, function; the function performed when each worker has finished their job 
    ##   - resetLastResults: bool (default= True); reset or not the last results
    ##

    ## TODO: adjust iterator parameter (removing it)
    def startMultiProcessing(self, job_list: list, callback= None, error_callback= None, resetLastResults = True, full_throttle = False, processes_number= None):
        if full_throttle:
            print("[WARNING] Full throttle mode enabled: using all logical cores. Timing accuracy may be affected.\n")
            parallel_processes = FULL_THROTTLE_PROCESS_COUNT
        elif processes_number:
            parallel_processes = min(processes_number, FULL_THROTTLE_PROCESS_COUNT)
            print(f"[Warning] The number of processes requested ({processes_number}) exceeds the number of processes in full throttle mode ({FULL_THROTTLE_PROCESS_COUNT}).")
        else:
            parallel_processes = SAFE_PROCESS_COUNT

        parallel_processes = min(parallel_processes, len(job_list))
        self.last_parallel_processes = parallel_processes
        print("[Info] Checking for others processes...")
        self.checkForAvailableMultiProcessing()
        aborted = False
        try:
            self.ordered_callbacks.reset()
            self.ordered_callbacks.set(callback, error_callback)
            print("[Status] Ok")
    
            
            if resetLastResults:
                print("[Warning] Resetting last multiproccessing results...")
                self.resetLastResults()
    
    
            print(f"[Info] Creating guard file at \"{self.guard_file_path}\"", "\n")
            guardFile = open(self.guard_file_path, "x")
            guardFile.close()
    
            print(f"[INFO] Launching pool with {parallel_processes} workers...")
            pool = mp.Pool(parallel_processes)
    
            for job_index, job in enumerate(job_list):
                args = job.get_args()
                kwargs = job.get_kwargs()
                function = job.get_function()
                high_priority = job.has_high_priority()
                if function is None:
                    raise ValueError(f"[ERROR] Job {job_index} missing function.")
                f_args = (function, job_index, args, kwargs, high_priority)
                print(f"[New Job] Queued job {job_index}: function= {function.__name__}")#, args={args}, kwargs={kwargs}") <- make reducible 
                cb = partial_callback(self.ordered_callbacks.execute, job_index)
                async_result = pool.apply_async(func=default_process_function, 
                                            args=(f_args,), 
                                            callback=cb,
                                            error_callback=cb)
                self.results.append(async_result)
                
        
            print("[Info] Closing processes pool...")
            pool.close()
    
            while True:
    
                if not os.path.exists(self.guard_file_path):
                    print("[ABORT] Guard file removed manually. Terminating pool...")
                    pool.terminate()
                    aborted = True
                    break
    
                if all([res.ready() for res in self.results]):
                    print("\nAll tasks completed!")
                    break
    
                time.sleep(0.5)
                
            pool.join()
               
        finally:
            if not aborted:
                print("[Info] Releasing guard file...")
                os.remove(self.guard_file_path)
            print("[Status] Ready")

    def startUniformMultiProcessing(self, function, job_args, callback=None, error_callback=None, high_priority= False, **options):
        arguments = []
        for job_arg in job_args:
            job_arg = job_arg.copy()
            job_arg.function = function
            job_arg.high_priority = high_priority
            arguments.append(job_arg)

        return self.startMultiProcessing(arguments, callback=callback, error_callback=error_callback, **options)


    def checkForAvailableMultiProcessing(self):
        assert not os.path.exists(self.guard_file_path), "[ERROR] Unable to start Multiprocessing.Pool, another already started!"

    def resetLastResults(self):
        self.results = []

    def getResults(self):
        return self.results

    def test_function(x): 
        print(f"Running test on {x}")
        return {"test": x}