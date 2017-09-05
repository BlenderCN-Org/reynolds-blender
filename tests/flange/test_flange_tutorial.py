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

class TestFlangeTutorial(TestFoamTutorial):
    def setUp(self):
        super(TestFlangeTutorial, self).setUp()
        self.tutorial_name = 'flange'
        self.test_module_dir = 'flange'
        self.copy_tutorial_case_dir(self.tutorial_name, self.test_module_dir)
        self.scene = bpy.context.scene

    def _add_flange_trisurface(self):
        self.scene.stl_file_path = os.path.join(self.temp_tutorial_dir,
                                                'constant',
                                                'triSurface', 'flange.stl')
        bpy.ops.reynolds.import_stl()
        self.assertIsNotNone(self.scene.geometries['Flange'])

    def _add_refine_hole(self):
        bpy.ops.object.select_all(False)
        bpy.ops.mesh.primitive_uv_sphere_add(size=0.0030,
                                             location=(0, -0.012, 0))

    def _add_blockmesh_to_flange_trisurface(self):
        bpy.ops.object.select_all(False)
        flange_obj = self.scene.objects['Flange']
        self.scene.objects.active = flange_obj
        bpy.ops.reynolds.add_geometry_block()
        self.assertIsNotNone(self.scene.objects['Cube'])
        blockmesh_obj = self.scene.objects['Cube']
        bpy.ops.object.select_all(False)
        self.switch_to_edit_mode(blockmesh_obj)
        self.select_case_dir('//flange')
        self.scene.convert_to_meters = 1
        self.select_vertices(blockmesh_obj, [0, 4, 5, 1, 2, 6, 7, 3])
        self.set_number_of_cells(20, 20, 20)
        self.set_grading(1, 1, 1)
        self.assign_blocks()
        patches = {'patch1': ([5], 'patch'),
                   'patch2': ([4], 'patch'),
                   'patch4': ([0, 2], 'patch'),
                   'patch3': ([3, 1], 'patch')}
        self.select_boundary(blockmesh_obj, patches)
        self.generate_blockmeshdict()
        self.run_blockmesh()

    def _add_flange_trisurface_geometry(self):
        flange_obj = self.scene.objects['Flange']
        self.scene.objects.active = flange_obj
        self.scene.geometry_type = 'triSurfaceMesh'
        self.scene.refinement_type = 'Surface'
        self.scene.refinement_level_min = 2
        self.scene.refinement_level_max = 2
        self.scene.has_features = True
        self.scene.feature_extract_included_angle = 150.0
        self.scene.feature_extract_ref_level = 0
        bpy.ops.shmd_geometries.list_action('INVOKE_DEFAULT', action='ADD')
        bpy.ops.reynolds.assign_shmd_geometry()
        self.assertEqual(self.scene.geometries['Flange']['type'],
                         'triSurfaceMesh')
        self.assertEqual(self.scene.geometries['Flange']['refinement_type'],
                         'Surface')
        self.assertEqual(self.scene.geometries['Flange']['refinementSurface']
                         ['min'], 2)
        self.assertEqual(self.scene.geometries['Flange']['refinementSurface']
                         ['max'], 2)
        self.assertTrue(self.scene.geometries['Flange']['has_features'])
        self.assertEqual(self.scene.geometries['Flange']['included_angle'],
                         150.0)
        self.assertEqual(self.scene.geometries['Flange']['feature_level'], 0)

    def _add_refine_hole_geometry(self):
        self.scene.objects.active = None
        sphere = self.scene.objects['Sphere']
        self.scene.objects.active = sphere
        bpy.context.object.name = 'refineHole'
        self.scene.geometry_type = 'searchableSphere'
        self.scene.refinement_type = 'Region'
        self.scene.refinement_mode = 'inside'
        self.scene.ref_reg_dist = 1e15
        self.scene.ref_reg_level = 3
        self.scene.has_features = False
        bpy.ops.shmd_geometries.list_action('INVOKE_DEFAULT', action='ADD')
        bpy.ops.reynolds.assign_shmd_geometry()
        self.assertIsNotNone(self.scene.geometries['refineHole'])
        self.assertEqual(self.scene.geometries['refineHole']['type'],
                         'searchableSphere')
        self.assertEqual(self.scene.geometries['refineHole']['refinement_type'],
                         'Region')
        self.assertAlmostEqual(self.scene.geometries['refineHole']['radius'],
                               0.00300000014)
        self.assertEqual(self.scene.geometries['refineHole']['refinementRegion']['mode'],
                         'inside')
        self.assertEqual(self.scene.geometries['refineHole']['refinementRegion']['level'], 3)
        self.assertAlmostEqual(self.scene.geometries['refineHole']['refinementRegion']['dist'],
                               999999986991104.0)

    def _mark_location_in_space(self):
        self.scene.location_in_mesh = [-9.23149e-05, -0.0025, -0.0025]

    def _generate_surface_features(self):
        bpy.ops.reynolds.generate_surface_dict()
        bpy.ops.reynolds.extract_surface_features()

    def _set_castellated_mesh_controls(self):
        self.scene.max_local_cells = 100000
        self.scene.max_global_cells = 2000000
        self.scene.min_refinement_cells = 0
        self.scene.max_load_unbalance = 0.0
        self.scene.n_cells_between_levels = 1
        self.scene.resolve_feature_angle = 30
        self.allow_free_standing_zones = True

    def _set_snapping_controls(self):
        self.scene.tolerance = 1
        self.scene.n_smooth_patch_iter = 3
        self.scene.disp_relax_iter = 300
        self.scene.snapping_relax_iter = 5
        self.scene.feature_edge_snapping_iter = 10
        self.scene.implicit_feature_snap = False
        self.scene.explicit_feature_snap = True
        self.scene.multi_region_feature_snap = True

    def _set_layers_controls(self):
        self.scene.relative_sizes = True
        self.scene.layer_name = '"flange_.*"'
        self.scene.n_surface_layers = 1
        bpy.ops.shmd_layers.list_action('INVOKE_DEFAULT', action='ADD')
        bpy.ops.reynolds.assign_layer()
        self.assertIsNotNone(self.scene.add_layers['"flange_.*"'])
        self.assertEqual(self.scene.add_layers['"flange_.*"'], 1)
        self.scene.expansion_ratio = 1
        self.scene.final_layer_thickness = 0.3
        self.scene.min_layer_thickness = 0.25
        self.scene.n_grow_layers = 0
        self.scene.layer_feature_angle = 30
        self.scene.smooth_layer_thickness = 10
        self.scene.max_face_thickness_ratio = 0.5
        self.scene.max_thickness_to_medial_ratio = 0.3
        self.scene.min_median_axis_angle = 90
        self.scene.n_buffer_cells_no_extrude = 0

    def _set_mesh_quality_controls(self):
        self.scene.max_internal_face_skewness = 4
        self.scene.min_pyramid_vol = 1e-13
        self.scene.min_tetrahedral_quality = 1e-15
        self.scene.min_face_twist = 0.02

    def _generate_snappyhexmeshdict(self):
        bpy.ops.reynolds.generate_shmd()

    def _run_snappyhexmesh(self):
        bpy.ops.reynolds.snappy_hexmesh_runner()

    def test_snappyhexmesh_with_flange_tutorial(self):
        # --------------
        # Initialization
        # --------------
        self.check_addon_loaded()
        self.start_openfoam()
        # -------------------
        # Steps to solve case
        # -------------------
        self._add_flange_trisurface()
        self._add_refine_hole()
        self._add_blockmesh_to_flange_trisurface()
        self._add_flange_trisurface_geometry()
        self._add_refine_hole_geometry()
        self._mark_location_in_space()
        self._generate_surface_features()
        self.check_imported_wavefront_objs()
        self._set_castellated_mesh_controls()
        self._set_snapping_controls()
        self._set_layers_controls()
        self._generate_snappyhexmeshdict()
        self._run_snappyhexmesh()
        self.solve_case('laplacianFoam');
        self.assertTrue(self.scene.case_solved)
        bpy.ops.wm.save_mainfile()

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFlangeTutorial)
unittest.TextTestRunner().run(suite)
