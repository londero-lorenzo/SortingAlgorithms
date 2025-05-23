import ArrayStorageCompressor as asc
import argparse, sys

def increment(string, reverse= False):
    try:
        number = int(string)
        number += 1 if not reverse else -1
    except Exception as e:
        print(f"Unable to convert parametric chars.")
        raise e
    return number

operations = {("{", "}"): lambda x: str(increment(x)), ("{+", "}"): lambda x: str(increment(x)), ("{-", "}"): lambda x: str(increment(x, reverse= True))}

    
    
def preprocessing(s, return_with_format= False, return_clean_string = False):
    processed_string = s
    next_format_string = s
    clean_string = s
    for k, operation in operations.items():
        starter_key, end_key = k
        while starter_key in processed_string and end_key in processed_string:
            key_start_position = processed_string.find(starter_key)
            key_end_position = processed_string.find(end_key)
            string_to_modify = processed_string[key_start_position+len(starter_key): key_end_position]
            first_chunk = processed_string[:key_start_position] 
            last_chunk = processed_string[key_end_position+len(end_key):]
            clean_string = first_chunk + string_to_modify + last_chunk
            processed_string = first_chunk + operation(string_to_modify) + last_chunk
            if return_with_format:
                next_format_string = first_chunk + starter_key + operation(string_to_modify)+ end_key + last_chunk
    
    if return_clean_string:
        return clean_string
        
    output = (processed_string,)
    if return_with_format:
        output += (next_format_string,)
   
    return output
    
def get_files_from_path_format(format_string, files_number):
    files = [preprocessing(format_string, return_clean_string= True)]
    next_format_string = format_string
    for _ in range(files_number-1):
        processed_string, next_format_string = preprocessing(next_format_string, return_with_format= True)
        if processed_string == next_format_string:
            break
        files.append(processed_string)
    return files

if __name__ == "__main__":
    decault_action = "--compress"
    parser = argparse.ArgumentParser("Compress/Decompress file")
    parser.add_argument("-f", "--file", help="Target file path, include '{+#}' or '{-#}' for select multiple files with same pattern name.\n'#' indicates the start number, '+' and '-' indicates the operation of increase and decrease of file selection.", type=str, default= None)
    parser.add_argument("-c", "--compress", help="Flag to compress.", action='store_true')
    parser.add_argument("-dec", "--decompress", help="Flag to decompress.", action='store_true')
    parser.add_argument("-r", "--range", help="Range of files with same pattern name.", type= int, default=1)
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    if args.file == None:
        print(f"Error, insert file path.")
        sys.exit(1)
        
    if not args.compress and not args.decompress or args.compress and args.decompress:
        current_args = sys.argv[1:]
        current_args.append(decault_action)
        print(f"Warning, both compress and decompress flags are {args.compress}. Default action: {decault_action.strip('--')}")
        proceed = input("Proceed? [Y/n]")
        if proceed == 'Y':
            args = parser.parse_args(current_args)
        else:
            sys.exit(1)
    for file in get_files_from_path_format(args.file, args.range):
        print(f"Working on: {file}")
        data = asc.readFromFile(file, decompress= args.decompress, load= False)
        asc.writeOnFile(data, file, compress= args.compress, dump= False)
    print("Done.")
    
    
