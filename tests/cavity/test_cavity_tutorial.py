import os
import pathlib
import unittest

import reynolds_blender

import bpy, bmesh

from tests.foam_test_case import TestFoamTutorial

class TestCavityTutorial(TestFoamTutorial):
    def setUp(self):
        super(TestCavityTutorial, self).setUp()
        self.tutorial_name = 'cavity'
        self.test_module_dir = 'cavity'
        self.copy_tutorial_case_dir(self.tutorial_name, self.test_module_dir)

    def test_blockmesh_with_cavity_tutorial(self):
        # test if addon got loaded correctly
        # every addon must provide the "bl_info" dict
        self.assertIsNotNone(reynolds_blender.bl_info)

        # self.copy_tutorial_case_dir();

        # -------------
        # get the scene
        # -------------
        scene = bpy.context.scene

        # --------------
        # start openfoam
        # --------------
        bpy.ops.reynolds.start_of()

        # -------------------
        # switch to edit mode
        # -------------------
        obj = scene.objects['Plane']
        scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # --------------------
        # select case directory
        # --------------------
        # use blender path format, the addon converts to abs path
        # // means current dir in blender path notation
        scene.case_dir_path = '//cavity'

        # ------------------
        # set convertToMeters
        # -------------------
        scene.convert_to_meters = 0.1

        # -------------------------------------------------------------
        # assign vertices with indices: 0, 1, 3, 2, 4, 5, 7, 6 in order
        # -------------------------------------------------------------
        bpy.ops.mesh.select_all(action='DESELECT')

        # ------------------------------------------------
        # Why is ensure_lookup_table() needed?
        # See https://developer.blender.org/rB785b90d7efd0
        # ------------------------------------------------

        bpy.ops.mesh.select_mode(type='VERT')
        for idx in  [0, 1, 3, 2, 4, 5, 7, 6]:
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

        # -----------------------------------------------
        # select all vertices in edit mode, assign blocks
        # -----------------------------------------------
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.reynolds.blocks()
        bpy.ops.mesh.select_all(action='DESELECT')

        # -------------------
        # set number of cells
        # -------------------
        scene.n_cells[0] = 20
        scene.n_cells[1] = 20
        scene.n_cells[2] = 1

        # -------------------------
        # set cell expansion ratios
        # -------------------------
        scene.n_grading[0] = 1
        scene.n_grading[1] = 1
        scene.n_grading[2] = 1

        # -----------------------------------------------------------------
        # set boundary
        # 1. select face with index 4 as movingWall, set name, type
        # 2. select face with index 3, 5, 2 as fixedWalls, set name, type
        # 3. select faces with indices 0, 1 as frontAndBack, set name, type
        # -----------------------------------------------------------------
        bpy.ops.mesh.select_mode(type='FACE')
        patches = {'movingWall': ([4], 'wall'),
                    'fixedWalls': ([3, 5, 2], 'wall'),
                    'frontAndBack': ([0, 1], 'empty')}
        for name, (faces, type) in patches.items():
            scene.region_name = name
            scene.region_type = type
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

        # ----------------------
        # generate blockMeshDict
        # ----------------------
        bpy.ops.reynolds.generate_bmd()

        # ---------------------
        # run blockMesh command
        # ---------------------
        bpy.ops.reynolds.block_mesh_runner()

        # ---------------
        # set solver name
        # ---------------
        scene.solver_name = 'icoFoam'

        # ----------
        # solve case
        # ----------
        bpy.ops.reynolds.solve_case()

        self.assertTrue(scene.case_solved)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCavityTutorial)
unittest.TextTestRunner().run(suite)
