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
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       IntVectorProperty,
                       FloatVectorProperty,
                       CollectionProperty
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       UIList
                       )
from bpy.path import abspath
from mathutils import Matrix, Vector

# --------------
# python imports
# --------------
import operator
import os

# ------------------------
# reynolds blender imports
# ------------------------

from reynolds_blender.gui.register import register_classes, unregister_classes
from reynolds_blender.gui.attrs import set_scene_attrs, del_scene_attrs
from reynolds_blender.gui.custom_operator import create_custom_operators
from reynolds_blender.gui.renderer import ReynoldsGUIRenderer
from reynolds_blender.block_cells import BlockMeshCellsOperator
from reynolds_blender.block_regions import BlockMeshRegionsOperator
from reynolds_blender.add_block import BlockMeshAddOperator

# ----------------
# reynolds imports
# ----------------
from reynolds.dict.parser import ReynoldsFoamDict
from reynolds.foam.cmd_runner import FoamCmdRunner

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

def generate_blockmeshdict(self, context):
    scene = context.scene
    obj = context.active_object

    # -------------------------
    # Start the console operatorr
    # --------------------------
    bpy.ops.reynolds.of_console_op()

    print("Select dir for generated blockmeshdict file")

    abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
    if abs_case_dir_path is None or abs_case_dir_path == '':
        self.report({'ERROR'}, 'Please select a case directory')
        return {'FINISHED'}

    if not scene.foam_started:
        self.report({'ERROR'}, 'Please start open foam')
        return {'FINISHED'}

    print(" ABSOLUTE CASE DIR PATH: ", abs_case_dir_path)

    if obj is None:
        self.report({'ERROR'}, 'Please select a block object')
        return {'FINISHED'}

    bbox = obj.bound_box
    x = [v[0] for v in obj.bound_box]
    x.sort()
    y = [v[2] for v in obj.bound_box]
    y.sort()
    z = [v[1] for v in obj.bound_box]
    z.sort()

    block_mesh_dict = ReynoldsFoamDict('blockMeshDict.foam')

    # generate bmd vertices
    bmd_vertices = []
    bmd_vertices.append([x[0], y[0], z[0]])
    bmd_vertices.append([x[7], y[0], z[0]])
    bmd_vertices.append([x[7], y[7], z[0]])
    bmd_vertices.append([x[0], y[7], z[0]])
    bmd_vertices.append([x[0], y[0], z[7]])
    bmd_vertices.append([x[7], y[0], z[7]])
    bmd_vertices.append([x[7], y[7], z[7]])
    bmd_vertices.append([x[0], y[7], z[7]])
    block_mesh_dict['vertices'] = bmd_vertices

    # generate bmd blocks
    bmd_blocks = []
    bmd_blocks.append('hex')
    bmd_blocks.append([0, 1, 2, 3, 4, 5, 6, 7])
    bmd_blocks.append([scene.n_cells[0], scene.n_cells[1],
                        scene.n_cells[2]])
    bmd_blocks.append('simpleGrading')
    grading_x = [[1, 1, scene.n_grading[0]]]
    grading_y = [[1, 1, scene.n_grading[1]]]
    grading_z = [[1, 1, scene.n_grading[2]]]
    grading = [grading_x, grading_y, grading_z]
    bmd_blocks.append(grading)
    print(bmd_blocks)
    block_mesh_dict['blocks'] = bmd_blocks

    # generate bmd regions
    bmd_boundary = []
    for name, r in scene.regions.items():
        name, patch_type, face_labels = r
        bmd_boundary.append(name)
        br = {}
        br['type'] = patch_type
        faces = []
        for f in face_labels:
            if f == 'Front':
                faces.append([0, 3, 2, 1])
            if f == 'Back':
                faces.append([4, 5, 6, 7])
            if f == 'Top':
                faces.append([3, 7, 6, 2])
            if f == 'Bottom':
                faces.append([0, 1, 5, 4])
            if f == 'Left':
                faces.append([0, 4, 7, 3])
            if f == 'Right':
                faces.append([1, 2, 6, 5])
        br['faces'] = faces
        bmd_boundary.append(br)
    print(bmd_boundary)

    if len(bmd_boundary) == 0:
        self.report({'ERROR'}, 'Please select regions/boundary conditions')
        return {'FINISHED'}

    block_mesh_dict['boundary'] = bmd_boundary

    # set convert to meters
    block_mesh_dict['convertToMeters'] = scene.convert_to_meters

    print("BLOCK MESH DICT")
    print(block_mesh_dict)

    bmd_file_path = os.path.join(abs_case_dir_path, "system", "blockMeshDict")
    with open(bmd_file_path, "w") as f:
        f.write(str(block_mesh_dict))

    return {'FINISHED'}

def run_blockmesh(self, context):
    scene = context.scene
    obj = context.active_object

    # -------------------------
    # Start the console operatorr
    # --------------------------
    bpy.ops.reynolds.of_console_op()

    print("Start openfoam")
    case_dir = bpy.path.abspath(scene.case_dir_path)

    if case_dir is None or case_dir == '':
        self.report({'ERROR'}, 'Please select a case directory')
        return {'FINISHED'}

    if not scene.foam_started:
        self.report({'ERROR'}, 'Please start open foam')
        return {'FINISHED'}

    block_file = os.path.join(case_dir, 'system', 'blockMeshDict')
    if not os.path.exists(block_file):
        self.report({'ERROR'}, 'Please generate blockMeshDict')
        return {'FINISHED'}

    scene.blockmesh_executed = False
    mr = FoamCmdRunner(cmd_name='blockMesh', case_dir=case_dir,
                        cmd_flags=['-blockTopology'])

    for info in mr.run():
        self.report({'WARNING'}, info)

    if mr.run_status:
        self.report({'INFO'}, 'Blockmesh -blockTopology: SUCCESS')
        # switch to layer 1
        context.scene.layers[0] = False
        context.scene.layers[1] = True
        block_obj_filepath = os.path.join(case_dir, 'blockTopology.obj')
        bpy.ops.import_scene.obj(filepath=block_obj_filepath)
        # switch back to layer 0
        context.scene.layers[1] = False
        context.scene.layers[0] = True
        # ensure imported obj is assigned to layer 1 only
        block_obj = context.scene.objects['blockTopology']
        for i in range(20):
            block_obj.layers[i] = (i == 1)
        mr = FoamCmdRunner(cmd_name='blockMesh', case_dir=case_dir)
        for info in mr.run():
            self.report({'WARNING'}, info)
        if mr.run_status:
            scene.blockmesh_executed = True
            self.report({'INFO'}, 'Blockmesh : SUCCESS')
        else:
            self.report({'ERROR'}, 'Blockmesh : FAILED')
    else:
        self.report({'ERROR'}, 'Blockmesh -blockTopology: FAILED')

    return{'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class BlockMeshDictPanel(Panel):
    bl_idname = "of_bmd_panel"
    bl_label = "BlockMesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator(BlockMeshAddOperator.bl_idname, text='', icon='PLUS')
        row.operator(BlockMeshCellsOperator.bl_idname, text='', icon='LATTICE_DATA')
        row.operator(BlockMeshRegionsOperator.bl_idname, text='', icon='MESH_PLANE')

        # ---------------------------------------
        # Render Block Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'block_mesh_panel.yaml')
        gui_renderer.render()

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('block_mesh_panel.yaml')
    create_custom_operators('block_mesh_panel.yaml', __name__)

def unregister():
    del_scene_attrs('block_mesh_panel.yaml')
    unregister_classes(__name__)

if __name__ == "__main__":
    register()
