import zipfile
import sys
import os

if __name__ == "__main__":
    with zipfile.ZipFile(sys.argv[1], mode='r') as zf:
        zf.extractall(os.path.dirname(sys.argv[1]))
