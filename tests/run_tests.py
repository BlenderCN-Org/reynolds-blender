import os
import glob
import subprocess
import sys
from subprocess import PIPE
from shutil import copy
from tempfile import mkdtemp

if sys.platform == 'linux' or sys.platform == 'linux2':
    blenderExecutable = 'blender'
elif sys.platform == 'darwin':
    blenderExecutable = '/Applications/Blender/blender.app/Contents/MacOS/blender'
else: #TODO: WINDOWS ???
    blenderExecutable == 'blender'

# allow override of blender executable (useful for CI, eg Travis)
if len(sys.argv) > 1:
    blenderExecutable = sys.argv[1]

# iterate over each *..blend file in the "tests" directory
# run blender with the .test.blend file and the corresponding .py python script
print(' ====================')
print(' RUN ADD ON TESTS ...')
print(' ====================')

dir_path = os.path.dirname(os.path.realpath(__file__))
search_file_pattern = dir_path + '/**/*.blend'

# -----------------------------------------------------------------------------
# Make temporary directories to store solved case dirs and blend files
# This is useful to investigate for errors and post processing with parafoam
# -----------------------------------------------------------------------------
# if not 'TRAVIS' in os.environ:
temp_tutorial_dir = mkdtemp()
case_dir = os.path.join(temp_tutorial_dir, 'case')
blend_dir = os.path.join(temp_tutorial_dir, 'blend')
if not os.path.exists(case_dir):
    os.makedirs(case_dir)
if not os.path.exists(blend_dir):
    os.makedirs(blend_dir)
os.environ['REYNOLDS_TEST_RUN_DIR'] = case_dir

# -------------
# Run the tests
# -------------
failures = 0
errors = 0
tests = 0

for blend_file in glob.glob(search_file_pattern):
    blend_filename = os.path.basename(blend_file)
    if not blend_filename.endswith('_copy.blend'):
        name, ext = os.path.splitext(blend_filename)
        blend_file_dir = os.path.dirname(blend_file)
        blend_temp_file = os.path.join(blend_file_dir, name + '_copy' + ext)
        print('blend temp file ', blend_temp_file)
        copy(blend_file, blend_temp_file)
        test_module = blend_file.replace('.blend', '.py')
        print('--------------------------------------------------')
        print('RUNNING TEST: ', test_module)
        fail = False
        with subprocess.Popen([blenderExecutable, '--addons', 'reynolds_blender',
                            '--factory-startup', '-noaudio', '-b',
                            blend_temp_file, '--python', test_module],
                            stdout=PIPE, stderr=PIPE,
                            universal_newlines=True) as p:
            tests += 1
            for info in p.stdout:
                print(info.rstrip('\n'))
            for info in p.stderr:
                print(info)
                # not fail ensures we don't double count failures/errors
                if not fail and 'FAIL' in info:
                    fail = True
                    failures += 1
                if not fail and 'ERROR' in info:
                    fail = True
                    errors += 1
        if fail:
            print('TEST FAILED')
            print('--------------------------------------------------')
        if not 'TRAVIS' in os.environ:
            copy(blend_temp_file, blend_dir)
        os.remove(blend_temp_file)

# -------------------
# Display output info
# -------------------
if not 'TRAVIS' in os.environ:
    print('The SOLVED case directories are available in : ', temp_tutorial_dir)

print('RESULT: TEST SUITE WITH {} TESTS'.format(tests))
if failures > 0 or errors > 0:
    print('FAILED WITH {} failures {} errors'.format(failures, errors))
    sys.exit(1)
else:
    print('PASSED')
    sys.exit(0)
