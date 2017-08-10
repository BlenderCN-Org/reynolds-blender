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

# -----------
# bpy imports
# -----------
import bpy, bmesh

# --------------
# python imports
# --------------
import os
import pathlib
import unittest

# ------------------------
# reynolds_blender imports
# ------------------------
from reynolds_blender import bl_info
from tests.foam_test_case import TestFoamTutorial

class TestCavityTutorial(TestFoamTutorial):
    def setUp(self):
        super(TestCavityTutorial, self).setUp()
        self.tutorial_name = 'cavity'
        self.test_module_dir = 'cavity'
        self.copy_tutorial_case_dir(self.tutorial_name, self.test_module_dir)
        self.scene = bpy.context.scene

    def test_blockmesh_with_cavity_tutorial(self):
        # --------------
        # Initialization
        # --------------
        self.check_addon_loaded()
        self.start_openfoam()
        obj = self.scene.objects['Plane']
        self.switch_to_edit_mode(obj)
        self.select_case_dir('//cavity')
        # -------------------
        # Steps to solve case
        # -------------------
        self.scene.convert_to_meters = 0.1
        self.select_vertices(obj, [0, 1, 3, 2, 4, 5, 7, 6])
        self.set_number_of_cells(20, 20, 1)
        self.set_grading(1, 1, 1)
        self.assign_blocks()
        self.select_boundary(obj)
        self.generate_blockmeshdict()
        self.run_blockmesh()
        self.scene.solver_name = 'icoFoam'
        self.solve_case();
        self.assertTrue(self.scene.case_solved)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCavityTutorial)
unittest.TextTestRunner().run(suite)
