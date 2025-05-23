import numpy as np


numpy_datatypes = [(8, np.int8), (16, np.int16), (32, np.int32), (64, np.int64)]


def getBitNumberRepresentationLength(number):
    return np.ceil(np.log(number) / np.log(2))

    
def __calculateMinimumExpensiveType(number, typeList):
    numberBitsNeeded = getBitNumberRepresentationLength(number)

    for typeRep in typeList:
        if numberBitsNeeded < typeRep[0]:
            return typeRep[1]
    
    raise Exception


def calculateMinimumExpensiveArrayType(maxArrayVariabilityNumber):
     
    try:
        return __calculateMinimumExpensiveType(maxArrayVariabilityNumber, numpy_datatypes)
    except:
        raise Exception(f"Unable to detect datatype for array representation!\nMAX_NUMBER_IN_SAMPLER_RANGE: {MAX_NUMBER_IN_SAMPLER_RANGE} > MAX_NUMBER_AVAILABLE: {np.pow(2, numpy_datatypes[-1][0])/2-1}")

        