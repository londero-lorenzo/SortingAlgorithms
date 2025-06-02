from typing_extensions import override
import numpy as np
from Utils import ArrayStorageCompressor
import os

def deep_compare(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return (False, a,b)
        return all(deep_compare(a[k], b[k]) for k in a)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return (False, a, b)
        return all(deep_compare(x, y) for x, y in zip(a, b))
    elif isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        return (np.array_equal(a, b), a, b)
    else:
        return (a == b, a,b)

def merge(data, new_data):
    if isinstance(data, list):
        if isinstance(new_data, list):
            data.extend(new_data)
        else:
            data.append(new_data)
    elif isinstance(data, np.ndarray):
        return np.append(data, [new_data], axis=0)
    elif isinstance(data, dict):
        assert isinstance(new_data, dict)
        for k, v in new_data.items():
            if k in data:
                data[k] = merge(data[k], v)
            else:
                data[k] = v
    else:
        return [data, new_data]
    return data

class BaseDataDictionary:
    def __init__(self, initial_data= {}):
        assert isinstance(initial_data, dict), f"Expected dict, got {type(initial_data)}" 
        self.data = initial_data.copy()
    # update(..., overwriting=False) lavora per riferimento sui contenuti già presenti.
    def update(self, data, overwriting=True):
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        if overwriting:
            self.data.update(data)
        else:
            self.data = merge(self.data, data)
    def ensure_existence(self, *path, placeholder= None, raise_error_if_not_exists= True):
        current_dict = self.data
        for key in path[:-1]:
            if key not in current_dict:
                if raise_error_if_not_exists:
                    raise ValueError(f"Key {key} not found in current execution data storage.")
                else:
                    current_dict[key] = {}
            current_dict = current_dict[key]
        if path[-1] not in current_dict:
            current_dict[path[-1]] = placeholder
    def clear(self):
        self.data= {}
    def get(self, key):
        return self.data.get(key)
    def keys(self):
        return list(self.data.keys())
    def values(self):
        return self.data.values()
    def items(self):
        return self.data.items()

    def __contains__(self, key):
        return key in self.data
        
    def __getitem__(self, key):
        return self.data[key]
    def __len__(self):
        return len(self.data)
        
"""

{
    "key_1": {
        "data": []
        "n": n
        ...
    }
}

"""

class ArraySampleCreationArguments:
    def __init__(self, n, m, rep, seeds, dtype):
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Field 'n' must be a positive integer.")
        if not isinstance(m, int) or m <= 0:
            raise ValueError(f"Field 'm' must be a positive integer.")
        if not isinstance(rep, int) or rep <= 0:
            raise ValueError(f"Field 'rep' must be a positive integer.")
        if not isinstance(seeds, list) or not seeds:
            raise ValueError(f"Field 'seeds' must be a non-negative integer.")
        try:
            np.dtype(dtype)
        except Exception:
            raise TypeError(f"Field 'dtype' is not a valid numpy dtype.")
        self.n = n
        self.m = m
        self.rep = rep
        self.seeds = seeds
        self.dtype = np.dtype(dtype)

    
    def get_length(self):
        return self.n

    def get_number_variability(self):
        return self.m

    def get_repetitions(self):
        return self.rep

    def get_generation_seeds(self):
        return self.seeds

    def get_data_type(self):
        return self.dtype

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f"length: {self.get_length()}, number variability: {self.get_number_variability()}, "\
        f"repetitions: {self.get_repetitions()}, seeds: {self.get_generation_seeds()}, dtype: {self.get_data_type()}"

    def to_dict(self, as_json=False):
        return {
            "n": self.n,
            "m": self.m,
            "rep": self.rep,
            "seeds": self.seeds,
            "dtype": self.dtype if not as_json else str(self.dtype)
        }

    def __hash__(self):
        return hash(tuple(self.to_dict()))
    

class ArraySample:

    def __init__(self, sample: list, creation_arguments: ArraySampleCreationArguments, variability):
        assert isinstance(sample, list), f"Expected list, got {type(sample)}."
        assert isinstance(creation_arguments, (dict, ArraySampleCreationArguments)), f"Creation arguments are expected as ArraySampleCreationArguments or dict, got {type(creation_arguments)}."
        assert isinstance(variability, int), f"Key variability is expected as int, got {type(variability)}."
        self.sample = sample
        self.creation_arguments = creation_arguments if isinstance(creation_arguments, ArraySampleCreationArguments) else ArraySampleCreationArguments(**creation_arguments)
        self.variability = variability

    def get_creation_arguments(self):
        return self.creation_arguments

    def get_sample(self):
        return self.sample

    def get_variability(self):
        return self.variability

    ## {"sample": [[23, 12, ..., 32, 12], [...], ..., [...],  }
    def __str__(self):
        return f"sample:\n{np.array2string(np.array(self.get_sample()), threshold=99)}, "\
        f"\ncreation arguments:\n{str(self.get_creation_arguments())}, "\
        f"\nvariability: {self.get_variability()}"

    def __hash__(self):
        return hash(self.get_creation_arguments())

    def to_dict(self):
        return {
            "sample": self.get_sample(),
            "creation_arguments": self.get_creation_arguments().to_dict(),
            "variability": self.get_variability()
        }



   

def assert_dict_with_ArraySample(data):
    for key, value in data.items():
        if not isinstance(value, ArraySample):
            raise ValueError(f"Entry for key {key} must be a ArraySample, got {type(value)}")

        
class ArraySampleContainer(BaseDataDictionary):

    def __init__(self, initial_data= {}):
        if isinstance(initial_data, ArraySampleContainer):
            initial_data = initial_data.data
        else:
            assert_dict_with_ArraySample(initial_data)
        
        super().__init__(initial_data)

    def update(self, data, **options):
        assert_dict_with_ArraySample(data)
        super().update(data, **options)

    ## interval is exclusive for the end: [start, end)
    def getIndeciesOfUniformlySubdividedArray(self, n_chunks, interval=None):
        """
        Suddivide le chiavi in `n_chunks` blocchi con (circa) lo stesso numero di elementi (n * rep).
        Evita l'uso di bisect, esegue la divisione con un solo passaggio lineare.
        """
        keys = self.keys(toSort=True)
        offset = 0
        if interval is not None:
            s, e = interval
            keys = keys[s:e]
            offset = s
    
        sizes = [self.get(k).get_creation_arguments().get_length() * self.get(k).get_creation_arguments().get_repetitions() for k in keys]
        total_elements = sum(sizes)
        target_per_chunk = total_elements / n_chunks
    
        chunks = []
        start = 0
        acc = 0
        for i, size in enumerate(sizes):
            acc += size
            if acc >= target_per_chunk and len(chunks) < n_chunks - 1:
                end = i + 1
                chunks.append((start + offset, end + offset))
                start = end
                acc = 0
    
        if start < len(keys):
            chunks.append((start + offset, len(keys) + offset))
        return chunks

    def subdivideArrayUniformly(self, n_chunks, returnWithData=True, interval=None):
        """
        Suddivide gli array in `n_chunks` blocchi basati sul numero totale di elementi (n * rep).
        Se returnWithData=True, ritorna un dict {key: entry} con i dati nei blocchi.
        Se False, ritorna una lista di liste di chiavi.
        """
        chunks = self.getIndeciesOfUniformlySubdividedArray(n_chunks, interval)
    
        if returnWithData:
            for start, end in chunks:
                keys = self.keys(toSort=True)[start:end]
                outputDict = {}
                for k in keys:
                    outputDict[k] = self.data[k]
                yield ArraySampleContainer(outputDict)
        else:
            outputKeys = []
            for start, end in chunks:
                keys = self.keys(toSort=True)[start:end]
                outputKeys.append(keys)
            return outputKeys

    def get_samples(self):
        return self.values()

    
    def get(self, key, byKey = True):
        if byKey:
            if key in self.keys():
                return self.data[key]
    
            raise IndexError(f"No '{key}' key found in {self.keys()}")
        else:
            if 0 <= key < len(self.keys()):
                return self.data[self.keys()[key]]
    
            raise IndexError(f"Index {key} out of range [0,{len(self.keys(toSort=False))})")
            

    def get_creation_arguments(self):
        creation_arguments = {}
        for key, sample in self.items():
            creation_arguments[int(key)] = sample.get_creation_arguments().to_dict(as_json=True)
        return creation_arguments
    
    def getFromIntervall(self, start, end):
        keys = self.keys()[start: end]
        return self.getFromKeys(keys)
    

    def getFromKeys(self, keys):
        intervallDict = {}
        for key in keys:
            intervallDict.update({key: self.data[key]})
        return intervallDict

    def keys(self, toSort=True, interval=None):
        keys = list(self.data.keys())
    
        if toSort:
            keys = sorted(keys)
    
        if interval:
            start, end = interval
            if not (0 <= start <= end <= len(keys)):
                raise IndexError(
                    f"Interval not valid. Selected: {interval}, Available: (0, {len(keys)})"
                )
            keys = keys[start:end]
    
        return keys

    def __eq__(self, other):
        return deep_compare(self.to_dict(), other.to_dict())

    def __hash__(self):
        return hash(tuple(self.values()))

    def to_dict(self):
        return {key: sample_array.to_dict() for key, sample_array in self.items()}

    def estimate_data_size_MB(self):
        total_bytes = 0
        for key, data in self.data.items():
            creation_arguments = data.get_creation_arguments()
            dtype = np.dtype(creation_arguments.get_data_type())
            element_size = dtype.itemsize
            num_elements = creation_arguments.get_length() * creation_arguments.get_repetitions()
            total_bytes += num_elements * element_size
        return total_bytes / (1024 ** 2)




def assert_execution_time_dict_metadata(raw_chunk_data):
    required_keys = {"data", "metadata"}
    
    for key, chunks in raw_chunk_data.items():
        for chunk in chunks.values():
            for chunk_row in chunk:
                if not isinstance(chunk_row, dict):
                    raise ValueError(f"Entry for key {key} must be a dictionary, got {type(chunk_row)}")
        
                missing = required_keys - chunk_row.keys()
                if missing:
                    raise ValueError(f"Entry for key {key} is missing required fields: {missing}")
                
                # Validazioni specifiche (facoltative ma consigliate)
                if not isinstance(chunk_row["data"], list) and not isinstance(chunk_row["data"], np.ndarray):
                    raise TypeError(f"Field 'data' for key {key} must be a list or ndarray.")
                
class ExecutionTimeDataStorage(BaseDataDictionary):

    def __init__(self, initial_data= None):
        initial_data = initial_data or {}
        super().__init__(initial_data)


    def update(self, algorithm, array_folder, execution_times):
        self.get_execution_times(
            algorithm = algorithm, 
            array_folder = array_folder,
            raise_error_if_not_exists = False
        ).extend(execution_times)

        
    def get_execution_times(self, algorithm, array_folder= None, raise_error_if_not_exists= True):
        if array_folder is None:
            self.ensure_existence(algorithm, placeholder= [], raise_error_if_not_exists=raise_error_if_not_exists)
            return self[algorithm]
        else:
            self.ensure_existence(algorithm, array_folder, placeholder=[], raise_error_if_not_exists=raise_error_if_not_exists)
            return self[algorithm][array_folder]

    def set_execution_times(self, algorithm, new_values, array_folder= None, raise_error_if_not_exists= True):
        
        if array_folder is None:
            self.ensure_existence(algorithm, placeholder=[], raise_error_if_not_exists=raise_error_if_not_exists)
            self.data[algorithm] = new_values
        else:
            self.ensure_existence(algorithm, array_folder, placeholder=[], raise_error_if_not_exists=raise_error_if_not_exists)
            self.data[algorithm][array_folder] = new_values
        

    def merge(self, other):
        assert isinstance(other, (ExecutionTimeDataStorage, dict)), f"Expected ExecutionTimeDataStorage or dictionary, got {type(other)}"

        if isinstance(other, dict):
            other = ExecutionTimeDataStorage(other)
        
        for other_algorithm, other_folders_dictionary in other.items():
            if other_algorithm not in self.data:
                self.set_execution_times(other_algorithm, new_values= other_folders_dictionary)
                continue

            for other_folder_path, other_execution_times_list in other_folders_dictionary.items():
                if other_folder_path not in self.get_execution_times(other_algorithm):
                    self.set_execution_times(other_algorithm, array_folder= other_folder_path, new_values= other_execution_times_list)
                    continue
                assert isinstance(other_execution_times_list, list), f"Expected list, got {type(other_execution_times_list)}"
                execution_times = self.get_execution_times(other_algorithm, other_folder_path)
                other_execution_times = other.get_execution_times(other_algorithm, other_folder_path)
                
                assert isinstance(execution_times, list), f"Expected list, got {type(execution_times)}"
                assert len(execution_times) == len(other_execution_times), f"Expected same sample execution number, expected {len(execution_times)}, got {len(other_execution_times)}"
                
                for current_execution_time, other_execution_time in zip(execution_times, other_execution_times):
                    assert isinstance(other_execution_time, ArrayExecutionTime), f"Expected ArrayExecutionTime, got {type(other_execution_time)}"
        
                    current_execution_time.extend(other_execution_time)
                    current_execution_time.compute_time_analysis()

    def to_dict(self):
        return {alg: {storage: [ext_time.to_dict() for ext_time in ext_times] for storage, ext_times in storage_dict.items()} for alg, storage_dict in self.items()}
#        for chunk_time in execution_times:

        

class TimeAnalysis:
    def __init__(self):
        self.mean = None
        self.sd = None
        self.quantiles = {}

    def compute_analysis(self, execution_times):
        
        execution_times = np.array(execution_times, dtype=np.float64).flatten()

        self.mean = np.mean(execution_times)
        self.sd = np.std(execution_times, ddof=1) 

        quantile_levels = [0.01, 0.25, 0.5, 0.75, 0.99]
        self.quantiles = {q: np.quantile(execution_times, q) for q in quantile_levels}


    def to_dict(self):
        return {
            "mean": self.mean,
            "sd": self.sd,
            "quantiles": self.quantiles
        }
    


class ArrayExecutionTime(ArraySample):
    # [ [...], [...], [...], [...], ... , [...] ]
    def __init__(self, execution_times, creation_arguments, variability):
        assert isinstance(execution_times, list), f"Expected list, got {type(execution_times)}"
        assert isinstance(creation_arguments, ArraySampleCreationArguments), f"Expected ArraySampleCreationArguments, got {type(creation_arguments)}"

        assert execution_times, f"Execution times must be a valid list"
        
        
        rep = creation_arguments.get_repetitions()
        if len(execution_times) == rep:
            execution_times = [execution_times]
        super().__init__(execution_times, creation_arguments, variability)

        
        self.time_analysis = TimeAnalysis()

    def compute_time_analysis(self):
        self.time_analysis.compute_analysis(self.get_sample())


    def extend(self, other):
        assert isinstance(other, ArrayExecutionTime), f"Expected ArrayExecutionTime, got {type(other)}"
        
        assert self.get_creation_arguments() == other.get_creation_arguments(), f"Other measurement data comes from an array with different creation arguments, expected {self.get_creation_arguments().__str__()}, got {other.get_creation_arguments().__str__()}"


        for execution_chunk in other.get_sample():
            if execution_chunk in self.get_sample():
                raise ValueError(f"Error: same execution times detected in:\n{str(self)}")
            else:
                self.get_sample().append(execution_chunk)
        

    def get_time_analysis(self):
        return self.time_analysis

        

class FoldersDataStorage(BaseDataDictionary):
                    
    def __init__(self, initial_data= None):
        if initial_data is None:
            initial_data = {}
        super().__init__(initial_data)

    def update(self, folder_path, array_sample_container):
        assert isinstance(array_sample_container, ArraySampleContainer), f"Impoted data expected as ArraySampleContainer, got {type(array_sample_container)}"
        self.ensure_existence(folder_path, placeholder=ArraySampleContainer(), raise_error_if_not_exists=False)
        
        self.data[folder_path].update(array_sample_container.data)
        

    def get_folder_paths(self):
        return list(self.data.keys())

    def get_by_folder(self, folder_path):
        return self.data[folder_path]
