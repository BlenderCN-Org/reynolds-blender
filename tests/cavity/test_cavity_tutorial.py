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
        self.create_tutorial_case_dir('cavity')
        self.scene = bpy.context.scene

    def _generate_fv_schemes(self):
        self.scene.ddt_schemes_default = 'Euler'
        self.scene.grad_schemes_default = 'Gauss linear'
        self.scene.grad_schemes_grad_p = 'Gauss linear'
        self.scene.div_schemes_default = 'none'
        self.scene.div_schemes_phi_U = 'Gauss linear'
        self.scene.lap_schemes_default = 'Gauss linear orthogonal'
        self.scene.interp_schemes_default = 'linear'
        self.scene.sngrad_schemes_default = 'orthogonal'
        bpy.ops.reynolds.of_fvschemes()

    def _generate_fv_solution(self):
        self.scene.solvers_p_solver = 'PCG'
        self.scene.solvers_p_preconditioner = 'DIC'
        self.scene.solvers_p_tolerance = 1e-06
        self.scene.solvers_p_relTol = 0.05
        self.scene.solvers_pfinal_p = 'none'
        self.scene.solvers_pfinal_relTol = 0
        self.scene.solvers_U_solver = 'smoothSolver'
        self.scene.solvers_U_smoother = 'symGaussSeidel'
        self.scene.solvers_U_tolerance = 1e-05
        self.scene.solvers_U_relTol = 0
        self.scene.piso_nCorrectors = 2
        self.scene.piso_nNonOrthogonalCorrectors = 0
        self.scene.piso_pRefCell = 0
        self.scene.piso_pRefValue = 0
        bpy.ops.reynolds.of_fvsolutionop()

    def _generate_controldict(self):
        self.scene.cd_start_from = 'startTime'
        self.scene.cd_start_time = 0
        self.scene.cd_stop_at = 'endTime'
        self.scene.cd_end_time = 0.5
        self.scene.cd_delta_time = 0.005
        self.scene.cd_write_control = 'timeStep'
        self.scene.cd_write_interval = 20
        self.scene.cd_purge_write = 0
        self.scene.cd_write_format = 'ascii'
        self.scene.cd_write_precision = 6
        self.scene.cd_write_compression = 'off'
        self.scene.cd_time_format = 'general'
        self.scene.cd_time_precision = 6
        self.scene.cd_runtime_modifiable = True
        bpy.ops.reynolds.of_controldict()

    def _generate_transport_properties(self):
        self.scene.tp_dt_scalar_elt1 = '[ 0 2 -1 0 0 0 0]'
        self.scene.tp_dt_scalar_elt2 = 0.01
        bpy.ops.reynolds.of_transportproperties()

    def _initialize_p(self):
        self.scene.time_props_dimensions['p'] = '[ 0 2 -2 0 0 0 0 ]'
        self.scene.time_props_internal_field['p'] = 'uniform 0'

    def _initialize_U(self):
        self.scene.time_props_dimensions['U'] = '[ 0 1 -1 0 0 0 0 ]'
        self.scene.time_props_internal_field['U'] = 'uniform (0 0 0)'

    def test_blockmesh_with_cavity_tutorial(self):
        # --------------
        # Initialization
        # --------------
        self.check_addon_loaded()
        self.start_openfoam()
        obj = self.scene.objects['Plane']
        self.switch_to_edit_mode(obj)
        self.select_case_dir(self.temp_tutorial_dir)
        # -------------------
        # Steps to solve case
        # -------------------
        self.scene.convert_to_meters = 0.1
        self.set_number_of_cells(20, 20, 1)
        self.set_grading(1, 1, 1)
        # -------------------
        # Configure case
        # -------------------
        self.set_solver_name('icoFoam')
        self._generate_fv_schemes()
        self._generate_fv_solution()
        self._generate_controldict()
        self._generate_transport_properties()
        # -----------------------------------------------------------------
        # set boundary
        # 1. select face with index 4 as movingWall, set name, type
        # 2. select face with index 3, 5, 2 as fixedWalls, set name, type
        # 3. select faces with indices 0, 1 as frontAndBack, set name, type
        # -----------------------------------------------------------------
        patches = {'movingWall': (['Top'], 'wall', {'p': {'type': 'zeroGradient'},
                                                    'U': {'type':'fixedValue', 'value':'uniform (1 0 0)'}}),
                   'fixedWalls': (['Bottom', 'Left', 'Right'], 'wall', {'p': {'type': 'zeroGradient'},
                                                                        'U': {'type': 'noSlip'}}),
                   'frontAndBack': (['Front', 'Back'], 'empty', {'p': {'type': 'empty'},
                                                                 'U': {'type': 'empty'}})}
        self._initialize_p()
        self._initialize_U()
        self.select_boundary(obj, patches)
        self.generate_blockmeshdict()
        self.generate_time_props()
        self.run_blockmesh()
        self.check_imported_wavefront_objs()
        self.solve_case('icoFoam');
        self.assertTrue(self.scene.case_solved)
        bpy.ops.wm.save_mainfile()

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCavityTutorial)
unittest.TextTestRunner().run(suite)
