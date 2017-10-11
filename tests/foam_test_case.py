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

# ----------
# bpy imports
# -----------
import bpy, bmesh

# --------------
# python imports
# --------------
from distutils.dir_util import copy_tree, remove_tree
import os
import pathlib
import unittest

# ------------------------
# reynolds_blender imports
# ------------------------
from reynolds_blender import bl_info

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

    def start_openfoam(self):
        bpy.ops.reynolds.start_of()

    def generate_blockmeshdict(self):
        bpy.ops.reynolds.generate_bmd()

    def generate_time_props(self):
        bpy.ops.reynolds.generate_time_props()

    def run_blockmesh(self):
        bpy.ops.reynolds.block_mesh_runner()

    def set_solver_name(self, solver_name):
        self.scene.solver_name = solver_name

    def solve_case(self, solver_name):
        self.set_solver_name(solver_name)
        bpy.ops.reynolds.solve_case()

    def set_number_of_cells(self, x, y, z):
        self.scene.n_cells[0] = x
        self.scene.n_cells[1] = y
        self.scene.n_cells[2] = z

    def set_grading(self, x, y, z):
        self.scene.n_grading[0] = x
        self.scene.n_grading[1] = y
        self.scene.n_grading[2] = z

    def select_boundary(self, obj, patches):
        for name, (faces, patch_type, time_prop_info) in patches.items():
            bpy.ops.regions.list_action('INVOKE_DEFAULT', action='ADD')
            self.scene.region_name = name
            self.scene.region_type = patch_type
            self.scene.select_front_face = False
            self.scene.select_back_face = False
            self.scene.select_top_face = False
            self.scene.select_bottom_face = False
            self.scene.select_left_face = False
            self.scene.select_right_face = False
            for f in faces:
                if f == 'Front':
                    self.scene.select_front_face = True
                if f == 'Back':
                    self.scene.select_back_face = True
                if f == 'Top':
                    self.scene.select_top_face = True
                if f == 'Bottom':
                    self.scene.select_bottom_face = True
                if f == 'Left':
                    self.scene.select_left_face = True
                if f == 'Right':
                    self.scene.select_right_face = True
            bpy.ops.reynolds.assign_region()
            for prop_type, props in time_prop_info.items():
                print(' Will now assign props for time prop : ' + prop_type)
                print( props)
                self.scene.time_prop_type = prop_type
                for k, val in props.items():
                    if k == 'type':
                        self.scene.time_prop_patch_type = val
                    if k == 'value':
                        self.scene.time_prop_value = val
                if 'value' not in props:
                    self.scene.time_prop_value = ""
                bpy.ops.reynolds.assign_time_prop()

    def switch_to_edit_mode(self, obj):
        self.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    def select_case_dir(self, dir_path):
        # use blender path format, the addon converts to abs path
        # // means current dir in blender path notation
        self.scene.case_dir_path = dir_path

    def check_addon_loaded(self):
        # test if addon got loaded correctly
        # every addon must provide the "bl_info" dict
        self.assertIsNotNone(bl_info)

    def check_imported_wavefront_objs(self):
        block_objs = [ob for ob in self.scene.objects if ob.layers[1]]
        self.assertTrue(len(block_objs) > 0)

    def tearDown(self):
        if self.temp_tutorial_dir:
            if not 'TRAVIS' in os.environ:
                post_test_run_dir = os.environ['REYNOLDS_POST_TEST_RUN_DIR']
                tutorial_dirname = os.path.basename(self.temp_tutorial_dir)
                post_run_tutorial_dir = os.path.join(post_test_run_dir,
                                                          tutorial_dirname)
                copy_tree(self.temp_tutorial_dir, post_run_tutorial_dir)
            print('Removing copied tutorial dir ', self.temp_tutorial_dir)
            remove_tree(self.temp_tutorial_dir)
