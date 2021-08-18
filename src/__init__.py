import sys

PYTHON_VERSION_MIN=(3,8)

dotjoin = lambda x: ".".join(map(str, x))

if sys.version_info < PYTHON_VERSION_MIN:
    raise ValueError(f"You are currently running python{dotjoin(sys.version_info[:3])}. "
            f"Please ensure that python{dotjoin(PYTHON_VERSION_MIN)}+ is \ninstalled "
            f"and that the 'PYTHON' variable in the Makefile is pointing to the correct version.")

