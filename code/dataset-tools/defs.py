import sys
import pathlib

path = str(pathlib.Path(__file__).parent.parent.resolve())

if path not in sys.path:
    sys.path.insert(1, path)
