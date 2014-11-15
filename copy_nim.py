from os.path import make_dirs, join as join_paths, isfile as is_file, exists as path_exists
import sys
from shutil import copy2 as clone_file


def file_exists(p):
    return is_file(p) and path_exists(p)

input_path = sys.argv[1]
output_path = sys.argv[2]

nim_binary = 'nim' + ('.exe' if sys.platform == 'win32' else '')
nimrod_binary = 'nimrod' + ('.exe' if sys.platform == 'win32' else '')

nim_input_path = join_paths(input_path, nim_binary)
nim_output_path = join_paths(output_path, nim_binary)
nimrod_input_path = join_paths(input_path, nimrod_binary)
nimrod_output_path = join_paths(output_path, nimrod_binary)

print('Working Variables:')
print('\t input_path: {0}'.format(input_path))
print('\t output_path: {0}'.format(output_path))
print('\t nim_binary: {0}'.format(nim_binary))
print('\t nimrod_binary: {0}'.format(nimrod_binary))
print('\t nim_input_path: {0}'.format(nim_input_path))
print('\t nim_output_path: {0}'.format(nim_output_path))
print('\t nimrod_input_path: {0}'.format(nimrod_input_path))
print('\t nimrod_output_path: {0}'.format(nimrod_output_path))
print('')

if file_exists(nim_input_path) and file_exists(nimrod_input_path):
    make_dirs(output_path)
    print('make_dirs({0})'.format(output_path))

    clone_file(nim_input_path, nim_output_path)
    print('clone_file({0}, {1})'.format(nim_input_path, nim_output_path))
    clone_file(nimrod_input_path, nimrod_output_path)
    print('clone_file({0}, {1})'.format(nimrod_input_path, nimrod_output_path))

else:
    sys.exit('Bad binary names')
