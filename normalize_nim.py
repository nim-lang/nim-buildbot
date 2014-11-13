import os.path as path
import sys
from shutil import copyfile
import os
import stat   

set_bits = False
if sys.platform in ['linux2', 'darwin', 'cygwin']:
    nim_binary = path.join(sys.argv[1], 'nim')
    nimrod_binary = path.join(sys.argv[1], 'nimrod')
    set_bits = True
elif sys.platform in ['win32']:
    nim_binary = path.join(sys.argv[1], 'nim.exe')
    nimrod_binary = path.join(sys.argv[1], 'nimrod.exe')
else:
    sys.exit("No suitable platform action found!")

if path.isfile(nim_binary) and path.exists(nim_binary):
    print("copyfile({0}, {1})".format(nim_binary, nimrod_binary))
    copyfile(nim_binary, nimrod_binary)
    if set_bits:
        st = os.stat(nim_binary)
        os.chmod(nimrod_binary, st.st_mode)
elif path.isfile(nimrod_binary) and path.exists(nimrod_binary):
    print("copyfile({0}, {1})".format(nimrod_binary, nim_binary))
    copyfile(nimrod_binary, nim_binary)
    if set_bits:
        st = os.stat(nimrod_binary)
        os.chmod(nim_binary, st.st_mode)
else:
    sys.exit("Bad binary names")
