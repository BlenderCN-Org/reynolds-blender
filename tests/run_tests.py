import os
import glob
import subprocess
import sys
from subprocess import PIPE

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

failures = 0
errors = 0
tests = 0
for file in glob.glob(search_file_pattern):
    test_module = file.replace('.blend', '.py')
    print('--------------------------------------------------')
    print('RUNNING TEST: ', test_module)
    fail = False
    with subprocess.Popen([blenderExecutable, '--addons', 'reynolds_blender',
                          '--factory-startup', '-noaudio', '-b',
                          file, '--python', test_module],
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

print('RESULT: TEST SUITE WITH {} TESTS'.format(tests))
if failures > 0 or errors > 0:
    print('FAILED WITH {} failures {} errors'.format(failures, errors))
    sys.exit(1)
else:
    print('PASSED')
    sys.exit(0)
