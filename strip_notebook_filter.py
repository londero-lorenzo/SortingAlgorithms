import sys
from nbconvert.preprocessors import ClearOutputPreprocessor, ClearMetadataPreprocessor
import nbformat

def main():
    nb = nbformat.read(sys.stdin, as_version=4)

    cp = ClearOutputPreprocessor()
    mp = ClearMetadataPreprocessor()

    nb, _ = cp.preprocess(nb, {})
    nb, _ = mp.preprocess(nb, {})

    nbformat.write(nb, sys.stdout)

if __name__ == '__main__':
    main()