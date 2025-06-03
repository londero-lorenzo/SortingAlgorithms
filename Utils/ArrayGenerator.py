import numpy as np
import os
import random
import fnmatch

from Utils import ArraySettings
from Utils import ArrayStorageCompressor
from Utils import ArrayDataManager


ARRAY_GENERATION_FILE = "generation_params.json"

# Function that creates a random array using a default numpy random generator
# Input:
#     n = Length of array,
#     m = Numbers variability,
#     c = center of the range variability,
#     dtype = type of generated numbers
# Ouput:
#     random interger array with size 'n' and number variability of 'm' as type of 'dtype'
def initialize_array(n, m, dtype, seed):
    rng = np.random.default_rng(None if seed is None else int(seed))
    return rng.integers(m, size=n).astype(dtype)



# Function that creates a list of random arrays using a default numpy random generator
# Input:
#     n = Length of array,
#     m = Numbers variability,
#     rep = number of arrays in list (default = 1), 
#     dtype = type of generated numbers (default = np.int64)
# Ouput:
#     random interger array with size 'n' and number variability of 'm' as type of 'dtype'
def sample(n, m, rep = 1, dtype= np.int64, seeds= None):
    if seeds is None:
        seeds = [None for _ in range(rep)]
    arraysGeneated = []
    for i in range(rep):
        currentGeneratedArray = initialize_array(n, m, dtype, seeds[i])
        arraysGeneated.append(currentGeneratedArray)

    return arraysGeneated


def setup_parameter_builder_environment():
    used_seeds = []

    def build_array_parameters(index, param_value, seed_pool):
        builder = ArraySettings.CREATION_ARRAY_ARGUMENTS(param_value)
        rep = builder.to_dict()["rep"]

        for r in range(rep):
            seed = ArraySettings.CREATION_DETERMINISTIC_SEED(param_value, index, r)

            if seed in seed_pool:
                print(f"[Warning] Seed {seed} already used at iteration {index}.")
                t = 1
                while seed in seed_pool:
                    seed = ArraySettings.CREATION_DETERMINISTIC_SEED(param_value + 3*index + 5*(index + t), index, r)
                    t += 1

            seed_pool.append(seed)

        builder.set_generation_seeds(seed_pool[len(used_seeds)-rep:])
        return builder.build()

    return lambda index, param_value, seed_pool=used_seeds: build_array_parameters(index, param_value, seed_pool)


def find_file(filename, search_root):
    matches = []

    for root, dirs, files in os.walk(search_root):
        for file in files:
            if fnmatch.fnmatch(file, filename) and file.endswith(".json"):
                full_path = os.path.join(root, file)
                matches.append(full_path)
    return matches



def generate_array_by_generation_files(file_paths, args):
    destination_folder = args.output
    extension = ArrayStorageCompressor.COMPRESS_EXTENSION if args.compress else ArrayStorageCompressor.PICKABLE_EXTENSION
    
    if destination_folder and not os.path.isdir(destination_folder):
        raise FileNotFoundError(f"Selected destination folder was not found.")
    
    file_generated_index = 0 if args.number > 1 else ""
    for generation_file_path in file_paths:
        if not args.output:
            destination_folder = os.path.dirname(generation_file_path)
            file_generated_index = 0 if args.number > 1 else ""
        
        first_generated_name_temp = args.prefix + str(file_generated_index) + extension
        
        if os.path.isfile(os.path.join(destination_folder, first_generated_name_temp)) and not args.overwrite:
            if not args.auto:
                raise FileExistsError(f"Array file '{first_generated_name_temp}' already exists in {destination_folder}")
            else:
                print(f"Warning: Files detected in {destination_folder}, folder skipped.")
                continue

        print(f"Reading creation file at: {generation_file_path}\n")
        array_sample_container_arguments_json = ArrayStorageCompressor.readFromFile(generation_file_path, as_json= True)

        print(f"Generation of sample arrays...")
        sample_container = ArrayDataManager.ArraySampleContainer()
        for variability_key, creation_arguments in array_sample_container_arguments_json.items():
            sample_creation_arguments = ArrayDataManager.ArraySampleCreationArguments(**creation_arguments)
            sample_container.update(
                {
                int(variability_key): 
                    ArrayDataManager.ArraySample(
                        sample = sample(**sample_creation_arguments.to_dict()),
                        creation_arguments = sample_creation_arguments,
                        variability = int(variability_key)
                    )
                }
            )
        
        chunked_sample_container = sample_container.subdivideArrayUniformly(args.number)
        
        print(f"Saving generated arrays at: {destination_folder}\n")
        for chunk in chunked_sample_container:
            file_name = args.prefix + str(file_generated_index) + extension
            
            file_path = os.path.join(destination_folder, file_name)
            
            if os.path.isfile(file_path) and not args.overwrite:
                raise FileExistsError(f"Array file '{file_name}' already exists in {destination_folder}")
                
    
            if args.overwrite:
                print(f"Overwriting {file_path}")
            else:
                print(f"Generated {file_path}")
                
            ArrayStorageCompressor.writeOnFile(
                data = chunk,
                path = file_path,
                compress = args.compress
            )
            print(f"Generated array chunk was saved in: {file_path}")
            if args.number > 1:
                file_generated_index += 1
            
        print()




if __name__ == "__main__":
    import argparse, sys
    # make auto flag
    parser = argparse.ArgumentParser("Create array from generation file")
    parser.add_argument("-f", "--file", help="Target file path, must be a json.", type=str, required=True)
    parser.add_argument("-o", "--output", help="Folder where the chunks array will be generetad.", type=str, default= None)
    parser.add_argument("-n", "--number", help="On how many files the array will be divided.", type=int, default = ArraySettings.MAX_ARRAY_SAVE_FILES)
    parser.add_argument("-p", "--prefix", help="File name prefix for each generated file.", type= str, default = ArraySettings.GET_COMPRESSED_ARRAY_FILE_NAME)
    parser.add_argument("-a", "--auto", help="Automatically generate the arrays by searching for the target file.", action='store_true')
    parser.add_argument("-s", "--searchFolder", help="Folder from which to search the target file (used with --auto).", type=str, default=".")
    parser.add_argument("-w", "--overwrite", help="Overwrites any existing files.", action='store_true')
    parser.add_argument("-c", "--compress", help="Compress each generated file.", action='store_true')
    
    args = parser.parse_args()



    if args.auto:
        matches = find_file(args.file, args.searchFolder)
        if len(matches) == 0:
            print(f"Error: no file named '{args.file}' found in '{args.searchFolder}'")
            sys.exit(1)
        if '*.' in args.file and args.file.count('.') > 1:
            raise ValueError("Pattern name not recognized.")
        generation_file_paths = find_file(args.file, args.searchFolder)
    else:
        generation_file_paths = args.file
            
    generate_array_by_generation_files(generation_file_paths, args)
