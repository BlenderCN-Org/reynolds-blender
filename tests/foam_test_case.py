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

    def run_blockmesh(self):
        bpy.ops.reynolds.block_mesh_runner()

    def solve_case(self, solver_name):
        self.scene.solver_name = solver_name
        bpy.ops.reynolds.solve_case()

    def set_number_of_cells(self, x, y, z):
        self.scene.n_cells[0] = x
        self.scene.n_cells[1] = y
        self.scene.n_cells[2] = z

    def set_grading(self, x, y, z):
        self.scene.n_grading[0] = x
        self.scene.n_grading[1] = y
        self.scene.n_grading[2] = z

    # ----------------------------
    # assign vertices with indices
    # -----------------------------
    def select_vertices(self, obj, indices):
        bpy.ops.mesh.select_all(action='DESELECT')

        # ------------------------------------------------
        # Why is ensure_lookup_table() needed?
        # See https://developer.blender.org/rB785b90d7efd0
        # ------------------------------------------------

        bpy.ops.mesh.select_mode(type='VERT')
        for idx in  indices:
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.verts.ensure_lookup_table()
            vertices = mesh.verts
            vertices[idx].select = True
            bpy.ops.vertices.list_action('EXEC_DEFAULT', action='ADD')
            bpy.ops.reynolds.assign_vertex()
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.verts.ensure_lookup_table()
            vertices = mesh.verts
            vertices[idx].select = False

    def assign_blocks(self):
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.reynolds.blocks()
        bpy.ops.mesh.select_all(action='DESELECT')

    def select_boundary(self, obj, patches):
        bpy.ops.mesh.select_mode(type='FACE')
        for name, (faces, type) in patches.items():
            self.scene.region_name = name
            self.scene.region_type = type
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.faces.ensure_lookup_table()
            for f in faces:
                mesh.faces[f].select = True
            bpy.ops.regions.list_action('INVOKE_DEFAULT', action='ADD')
            bpy.ops.reynolds.assign_region()
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.faces.ensure_lookup_table()
            for f in faces:
                mesh.faces[f].select = False

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
