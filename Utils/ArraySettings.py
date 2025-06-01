import os
import numpy as np
from datetime import datetime
from enum import Enum
import time
from Utils import ArrayCalculateTypes
from Utils.ArrayStorageCompressor import ARRAY_ADMISSIBLE_EXTENSIONS


class Variability(Enum):
    onLength = dict(
        code = "N",
        nice_name = "Array length",
        MINIMUN_ARRAY_LENGTH = 100,
        MAXIMUM_ARRAY_LENGTH = 10**5,
        MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY = 10**5,
        MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY = 10**5,

        
        ARRAY_START_KEY = "MINIMUN_ARRAY_LENGTH",
        ARRAY_END_KEY = "MAXIMUM_ARRAY_LENGTH",
        ## arguments order: array length, array number variability
        CREATION_ARRAY_ARGUMENTS = lambda variability_number: (variability_number, Variability.onLength.value["MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY"])
        
    )

    onNumbers = dict(
        code = "M",
        nice_name = "Different numbers",
        MINIMUN_ARRAY_LENGTH = 10**4,
        MAXIMUM_ARRAY_LENGTH = 10**4,
        MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY = 10,
        MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY = 10**6,

        
        ARRAY_START_KEY = "MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY",
        ARRAY_END_KEY = "MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY",
        ## arguments order: array length, array number variability
        CREATION_ARRAY_ARGUMENTS = lambda variability_number: (Variability.onNumbers.value["MAXIMUM_ARRAY_LENGTH"], variability_number)
    )


### ---- VARIABILITY CHANGE ----
# change this in order to have variability on length of array or on the different numbers in array
VARIABILITY = Variability.onNumbers

NUMBER_OF_SAMPLES = 100
NUMBER_OF_REPETITIONS = 10
###


MAIN_ARRAY_STORAGE_FOLDER_PATH = os.path.join("Array", "ArrayStorage", f"{VARIABILITY.value['code']}_variability")
ARRAY_STORAGE_FOLDER_PREFIX = "storage_"

def GET_ARRAY_STORAGE_FOLDER_PATH(folder_name=None, get_all=False):
    main_storage_folder = MAIN_ARRAY_STORAGE_FOLDER_PATH
    folder_list = sorted(
        [
            f
            for f in os.listdir(main_storage_folder)
            if f.startswith(ARRAY_STORAGE_FOLDER_PREFIX)
            and os.path.isdir(os.path.join(main_storage_folder, f))
        ],
        reverse=True
    )
    assert folder_list, f"No storage folders found in {main_storage_folder}"
    if get_all and not folder_name:
        return [os.sep.join([main_storage_folder, folder]) for folder in folder_list]
        
    selected_folder = folder_name or folder_list[0]

    assert selected_folder in folder_list, f"No storage folder named {selected_folder} found in {main_storage_folder}"

    return [os.sep.join([main_storage_folder, selected_folder])]

def GET_COMPRESSED_ARRAY_FILES_IN_STORAGE_FOLDER(storage_folders= None, get_all= False):
    if storage_folders is None:
        storage_folders = [storage_folders]
    folders = []
    for folder in storage_folders:
        f = GET_ARRAY_STORAGE_FOLDER_PATH(folder_name= folder, get_all= get_all)
        folders.extend(f)
    output = []
    for folder in folders:
        for ext in ARRAY_ADMISSIBLE_EXTENSIONS:
            array_storage_file = os.path.join(folder, GET_COMPRESSED_ARRAY_FILE_NAME + ext)
            if os.path.exists(array_storage_file):
                break
        if os.path.isfile(array_storage_file):
            output.append(array_storage_file)
    return output
    
def CREATE_ARRAY_STORAGE_FOLDER():
    path = os.sep.join([
        MAIN_ARRAY_STORAGE_FOLDER_PATH,
        ARRAY_STORAGE_FOLDER_PREFIX + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")])
    os.makedirs(path, exist_ok=False)
    return path

GET_COMPRESSED_ARRAY_FILE_NAME = "ArrayStorage"


MAX_ARRAY_SAVE_FILES = 1

MINIMUN_ARRAY_LENGTH = VARIABILITY.value["MINIMUN_ARRAY_LENGTH"]
MAXIMUM_ARRAY_LENGTH = VARIABILITY.value["MAXIMUM_ARRAY_LENGTH"]

MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY = VARIABILITY.value["MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY"]
MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY = VARIABILITY.value["MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY"]

## variables used to calculate current 'a','b' coefficients
ARRAY_START_KEY = VARIABILITY.value[VARIABILITY.value["ARRAY_START_KEY"]]
ARRAY_END_KEY = VARIABILITY.value[VARIABILITY.value["ARRAY_END_KEY"]]




MAX_NUMBER_IN_SAMPLER_RANGE = MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY -1 ## -1 because the zero is included
MIN_NUMBER_IN_SAMPLER_RANGE = MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY

ARRAY_DATATYPE = ArrayCalculateTypes.calculateMinimumExpensiveArrayType(MAX_NUMBER_IN_SAMPLER_RANGE)

# argument order: array length, array number variability, array repetition based on VARIABILITY, dtype
def CREATION_ARRAY_ARGUMENTS(variability_number):
    n, m, rep, dtype = (*VARIABILITY.value["CREATION_ARRAY_ARGUMENTS"](variability_number), NUMBER_OF_REPETITIONS, ARRAY_DATATYPE)
    return int(n), int(m), int(rep), dtype

CREATION_DETERMINISTIC_SEED = lambda key, index, repetition: int(100 + key * NUMBER_OF_REPETITIONS + index + repetition + (time.time()*1000) % 100000) % (2**32 - 1) 

## class containing current settings, this class is used when static keywords are not allowed
class ArraySettings:

    settings = {}
    
    def __init__(self):
        pass
       
    def add(self, key, value):
        self.settings.update({key: value})
        
    def get(self, key):
        return self.settings[key]
       



CURRENT_SETTINGS = ArraySettings()
CURRENT_SETTINGS.add("NUMBER_OF_SAMPLES", NUMBER_OF_SAMPLES)
CURRENT_SETTINGS.add("NUMBER_OF_REPETITIONS", NUMBER_OF_REPETITIONS)
CURRENT_SETTINGS.add("MINIMUN_ARRAY_LENGTH", MINIMUN_ARRAY_LENGTH)
CURRENT_SETTINGS.add("MAXIMUM_ARRAY_LENGTH", MAXIMUM_ARRAY_LENGTH)
CURRENT_SETTINGS.add("MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY", MINIMUM_DIFFERENT_NUMBERS_IN_ARRAY)
CURRENT_SETTINGS.add("MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY", MAXIMUM_DIFFERENT_NUMBERS_IN_ARRAY)
