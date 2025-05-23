import zpaq
import pickle
import json

COMPRESS_EXTENSION = ".zpaq"
PICKABLE_EXTENSION = ".pick"
ARRAY_ADMISSIBLE_EXTENSIONS = [COMPRESS_EXTENSION, PICKABLE_EXTENSION]
JSON_EXTENSION = ".json"

def action(compress=False, decompress=False, dump=False, load=False):
    if compress and decompress:
        raise ValueError("You cannot use compression and decompression at the same time.")
    if dump and load:
        raise ValueError("You cannot use dump and load at the same time.")

    def composed(x):
        if dump:
            x = pickle.dumps(x, pickle.HIGHEST_PROTOCOL)
        if compress:
            x = zpaq.compress(x)
        if decompress:
            x = zpaq.decompress(x)
        if load:
            x = pickle.loads(x)
        return x

    return composed


def writeOnFile(data, path, return_file_path= False, compress= False, dump= True, as_json=False):

    if as_json:
        data = json.dumps(data, indent= 4).encode('utf-8')
        
        
    else:
        ## delete action function
        data = action(compress= compress, dump= dump)(data)
            
    if '.' not in path:
        if as_json:
            path += JSON_EXTENSION
        elif dump:
            path += PICKABLE_EXTENSION
        elif compress:
            path += COMPRESS_EXTENSION
            
            
    with open(path, "wb") as file:
        file.write(data)
        
    return path if return_file_path else None
    
def readFromFile(path, return_file_name= False, decompress= False, load= True, as_json=False):
        
    with open(path, "rb") as file:
        raw = file.read()

    if as_json:
        data = json.loads(raw.decode("utf-8"))
    else:
        data = action(decompress=decompress, load=load)(raw)

    return (data, path) if return_file_name else data
        

