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

    def generate_fv_schemes(self):
        self.scene.ddt_schemes_default = 'Euler'
        self.scene.grad_schemes_default = 'Gauss linear'
        self.scene.grad_schemes_grad_p = 'Gauss linear'
        self.scene.div_schemes_default = 'none'
        self.scene.div_schemes_phi_U = 'Gauss linear'
        self.scene.lap_schemes_default = 'Gauss linear orthogonal'
        self.scene.interp_schemes_default = 'linear'
        self.scene.sngrad_schemes_default = 'orthogonal'
        bpy.ops.reynolds.of_fvschemes()

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
        self.set_number_of_cells(20, 20, 1)
        self.set_grading(1, 1, 1)
        # -----------------------------------------------------------------
        # set boundary
        # 1. select face with index 4 as movingWall, set name, type
        # 2. select face with index 3, 5, 2 as fixedWalls, set name, type
        # 3. select faces with indices 0, 1 as frontAndBack, set name, type
        # -----------------------------------------------------------------
        patches = {'movingWall': (['Top'], 'wall'),
                   'fixedWalls': (['Bottom', 'Left', 'Right'], 'wall'),
                   'frontAndBack': (['Front', 'Back'], 'empty')}
        self.select_boundary(obj, patches)
        self.generate_blockmeshdict()
        self.run_blockmesh()
        self.check_imported_wavefront_objs()
        self.set_solver_name('icoFoam')
        self.generate_fv_schemes()
        self.solve_case('icoFoam');
        self.assertTrue(self.scene.case_solved)
        bpy.ops.wm.save_mainfile()

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCavityTutorial)
unittest.TextTestRunner().run(suite)
