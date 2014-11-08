import os.path as path
import sys
from shutil import copyfile


if sys.platform in ['linux2', 'darwin', 'cygwin']:
    nim_binary = 'nim'
    nimrod_binary = 'nimrod'
elif sys.platform in ['win32']:
    nim_binary = 'nim.exe'
    nimrod_binary = 'nimrod.exe'
else:
    sys.exit("No suitable platform action found!")

if path.fileexists(nim_binary):
    copyfile(nim_binary, nimrod_binary)
elif path.fileexists(nimrod_binary):
    copyfile(nimrod_binary, nim_binary)
