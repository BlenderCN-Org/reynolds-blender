#------------------------------------------------------------------------------
# Reynolds-Blender | The Blender add-on for Reynolds, an OpenFoam toolbox.
#------------------------------------------------------------------------------
# Copyright|
#------------------------------------------------------------------------------
#     Deepak Surti       (dmsurti@gmail.com)
#     Prabhu R           (IIT Bombay, prabhu@aero.iitb.ac.in)
#     Shivasubramanian G (IIT Bombay, sgopalak@iitb.ac.in)
#------------------------------------------------------------------------------
# License
#
#     This file is part of reynolds-blender.
#
#     reynolds-blender is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     reynolds-blender is distributed in the hope that it will be useful, but
#     WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#     Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with reynolds-blender.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

from distutils.dir_util import copy_tree, remove_tree
import os
import pathlib
import unittest

class TestFoamTutorial(unittest.TestCase):
    def setUp(self):
        self.current_dir = os.path.dirname(os.path.realpath(__name__))
        self.temp_tutorial_dir = None

    def copy_tutorial_case_dir(self, tutorial_name, test_module_dir):
        self.temp_tutorial_dir = os.path.join(self.current_dir,
                                              'tests', self.test_module_dir,
                                              self.tutorial_name)
        if not os.path.exists(self.temp_tutorial_dir):
            print('Creating temp tutorial dir: ', self.temp_tutorial_dir)
            pathlib.Path(self.temp_tutorial_dir).mkdir(parents=True,
                                                       exist_ok=True)
        tests_parent_dir = os.path.dirname(os.path.realpath('tests'))
        case_dir = os.path.join(tests_parent_dir, 'tests', 'tutorials',
                                self.tutorial_name)
        copy_tree(case_dir, self.temp_tutorial_dir)

    def tearDown(self):
        if self.temp_tutorial_dir:
            print('Removing copied tutorial dir ', self.temp_tutorial_dir)
            remove_tree(self.temp_tutorial_dir)
