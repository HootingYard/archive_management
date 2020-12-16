# rmdir.py -- recursively remove a directory. Marginally safer than "rm -rf".
#
import os
import shutil
import sys

assert len(sys.argv) == 2
assert " " not in sys.argv[1]
DIR = sys.argv[1]
if os.path.exists(DIR):
    shutil.rmtree(DIR)
