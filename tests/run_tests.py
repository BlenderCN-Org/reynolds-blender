import os
import glob
import subprocess
import sys

if sys.platform == 'linux' or sys.platform == 'linux2':
    blenderExecutable = 'blender'
elif sys.platform == 'darwin':
    blenderExecutable = '/Applications/Blender/blender.app/Contents/MacOS/blender'
else: #TODO: WINDOWS ???
    blenderExecutable == 'blender'

# allow override of blender executable (important for CI!)
if len(sys.argv) > 1:
    blenderExecutable = sys.argv[1]

# iterate over each *.test.blend file in the "tests" directory
# and open up blender with the .test.blend file and the corresponding .test.py python script
print(' RUN TESTS ...')

dir_path = os.path.dirname(os.path.realpath(__file__))
search_file_pattern = dir_path + '/**/*.blend'

for file in glob.glob(search_file_pattern):
    test_module = file.replace('.blend', '.py')
    print('RUNNING TEST: ', test_module)
    subprocess.call([blenderExecutable, '--addons', 'reynolds_blender',
                     '--factory-startup', '-noaudio', '-b',
                     file, '--python', test_module])
