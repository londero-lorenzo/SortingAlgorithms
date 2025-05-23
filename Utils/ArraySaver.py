import os
import sys
from datetime import datetime

from Utils.ArraySettings import VARIABILITY_CODE
from Utils.ArrayStorageCompressor import ARRAY_ADMISSIBLE_EXTENSIONS

# === COSTANTI ===

# Project root path
PROJECT_ROOT = sys.path[0]

# Prefisso cartelle di storage
ARRAY_STORAGE_FOLDER_PREFIX = "storage_"

# Prefisso e estensione dei file compressi
COMPRESSED_ARRAY_FILE_PREFIX = "ArrayStorageChunk_"

# Numero massimo di file salvati per array
MAX_ARRAY_SAVE_FILES = 20


MAIN_ARRAY_STORAGE_FOLDER_PATH = os.path.join(PROJECT_ROOT, "Array", "ArrayStorage", f"{ArraySettings.VARIABILITY_CODE}_variability")

def create_array_file_name(index):
    return COMPRESSED_ARRAY_FILE_PREFIX + str(index)"

    
def get_array_storage_folder_path(folder_name=None, get_all=False):
    folder_list = sorted(
        [
            file
            for file in os.listdir(MAIN_ARRAY_STORAGE_FOLDER_PATH)
            if file.startswith(ARRAY_STORAGE_FOLDER_PREFIX)
            and os.path.isdir(os.path.join(MAIN_ARRAY_STORAGE_FOLDER_PATH, file))
        ],
        reverse=True
    )
    
    assert folder_list, f"No storage folders found in {MAIN_ARRAY_STORAGE_FOLDER_PATH}"
    
    if get_all and folder_name is None:
        return [os.sep.join([main_storage_folder, folder]) for folder in folder_list]
        
    selected_folder = folder_name or folder_list[0]

    assert selected_folder in folder_list, f"No storage folder named {selected_folder} found in {main_storage_folder}"

    return os.sep.join([main_storage_folder, selected_folder])

def GET_COMPRESSED_ARRAY_FILES_IN_STORAGE_FOLDER(project_root, storage_folders= [None], get_all= False):
    folders = []
    for folder in storage_folders:
        f = GET_ARRAY_STORAGE_FOLDER_PATH(project_root, folder_name= folder, get_all= get_all)
        if isinstance(f, list):
            folders.extend(f)
        else:
            folders.append(f)
            
    output = {}
    for folder in folders:
        output.update({folder : [file for file in os.listdir(folder) if file[file.rfind('.'):] in ARRAY_ADMISSIBLE_EXTENSIONS]})
    return output
    
def CREATE_ARRAY_STORAGE_FOLDER(project_root):
    path = os.sep.join([
        MAIN_ARRAY_STORAGE_FOLDER_PATH(project_root),
        ARRAY_STORAGE_FOLDER_PREFIX + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")])
    os.makedirs(path, exist_ok=False)
    return path

COMPRESSED_ARRAY_FILE_PREFIX = "ArrayStorageChunk_"
COMPRESSED_ARRAY_FILE_EXTENSTION = ".zpaq"
CREATE_COMPRESSED_ARRAY_FILE_NAME = lambda index: COMPRESSED_ARRAY_FILE_PREFIX + str(index) + COMPRESSED_ARRAY_FILE_EXTENSTION


MAX_ARRAY_SAVE_FILES = 20
