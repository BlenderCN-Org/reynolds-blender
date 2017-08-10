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

# ----------------
# reynolds imports
# ----------------
from reynolds.dict.parser import ReynoldsFoamDict
from reynolds.foam.cmd_runner import FoamCmdRunner

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

def assign_blocks(self, context):
    scene = context.scene
    obj = context.active_object

    # print the values to the console
    print("Assigning blocks ", scene.vertex_labels)

    mode = bpy.context.active_object.mode
    # switch from Edit mode to Object mode so the selection gets updated
    bpy.ops.object.mode_set(mode='OBJECT')

    hex = []
    for v in obj.data.vertices:
        if v.select:
            print('selected v for blocks: ', v.index)
            print(scene.vertex_labels[v.index])
            hex.append(scene.vertex_labels[v.index])
            print(hex)

    hex.sort()
    print("blocks hex: ", hex)
    scene.blocks.clear()
    scene.blocks.extend(hex)
    print("scene hex: ", hex    )
    # reset mode
    bpy.ops.object.mode_set(mode=mode)
    return {'FINISHED'}

def assign_vertex(self, context):
    scene = context.scene
    obj = context.active_object

    print("Assigning vertex ", scene.vertex_labels)

    mode = bpy.context.active_object.mode
    # switch from Edit mode to Object mode so the selection gets updated
    bpy.ops.object.mode_set(mode='OBJECT')

    print(scene.bmd_vertices, scene.bmd_vindex)
    for v in obj.data.vertices:
        if v.select:
            print("Selected vertex: ", v.index)
            if not v.index in scene.vertex_labels:
                item = scene.bmd_vertices[scene.bmd_vindex]
                item.name = "Vertex " + str(v.index)
                scene.vertex_labels[v.index] = scene.bmd_vindex

    print(scene.vertex_labels)
    # reset mode
    bpy.ops.object.mode_set(mode=mode)
    return{'FINISHED'}

def remove_vertex(self, context):
    print("Removing assigned vertex")

    scene = context.scene
    obj = context.active_object

    print(scene.bmd_vindex, scene.bmd_vertices[scene.bmd_vindex])
    item = scene.bmd_vertices[scene.bmd_vindex]
    _, v_index = item.name.split("Vertex ", 1)
    v_index = int(v_index)
    item.name = ""
    print(scene.vertex_labels)
    scene.vertex_labels.pop(v_index, None)
    print(scene.vertex_labels)
    return{'FINISHED'}

def assign_region(self, context):
    print("Assigning region")

    scene = context.scene
    obj = context.active_object

    bm = bmesh.from_edit_mesh(obj.data)

    r_faces = []

    for f in bm.faces:
        if f.select:
            print("Selected face: ", f.index, f)
            print("normal ", f.normal, f.normal.magnitude)

            print (obj.data.polygons[f.index].vertices)
            f_vertex_labels = []
            p = obj.data.polygons[f.index]
            r_vertices = []
            for v_index in p.vertices:
                r_vertices.append(v_index)
            print(r_vertices)
            r_vertices.reverse()
            print(r_vertices)
            f_vertex_labels = []
            for v in r_vertices:
                f_vertex_labels.append(scene.vertex_labels[v])
            print(f_vertex_labels)
            r_faces.append(f_vertex_labels)

    print(r_faces)
    item = scene.bmd_regions[scene.bmd_rindex]
    region_name = scene.region_name
    face_str = region_name + " : " + ' '.join(str(f) for f in r_faces)
    r = (scene.region_name, scene.region_type, r_faces)
    item.name = face_str
    scene.regions[region_name] = r
    print(scene.regions)
    return{'FINISHED'}

def remove_region(self, context):
    print("Removing region")

    scene = context.scene
    obj = context.active_object

    print(scene.bmd_rindex, scene.bmd_regions[scene.bmd_rindex])
    item = scene.bmd_regions[scene.bmd_rindex]
    r_name, _ = item.name.split(" : ", 1)
    scene.regions.pop(r_name, None)
    item.name = ""
    return{'FINISHED'}

def generate_blockmeshdict(self, context):
    scene = context.scene
    obj = context.active_object

    print("Select dir for generated blockmeshdict file")

    abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)

    block_mesh_dict = ReynoldsFoamDict('blockMeshDict.foam')

    # generate bmd vertices
    bmd_vertices = []
    sorted_labels = sorted(scene.vertex_labels.items(),
                            key=operator.itemgetter(1))
    for v_index, _ in sorted_labels:
        v = obj.data.vertices[v_index].co
        print(v)
        bmd_v = [v.x, v.z, v.y] # Swap y, z
        bmd_vertices.append(bmd_v)
    block_mesh_dict['vertices'] = bmd_vertices

    # generate bmd blocks
    bmd_blocks = []
    bmd_blocks.append('hex')
    bmd_blocks.append(scene.blocks)
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
            faces.append(f)
        br['faces'] = faces
        bmd_boundary.append(br)
    print(bmd_boundary)
    block_mesh_dict['boundary'] = bmd_boundary

    # set convert to meters
    block_mesh_dict['convertToMeters'] = scene.convert_to_meters

    print("BLOCK MESH DICT")
    print(block_mesh_dict)

    bmd_file_path = os.path.join(abs_case_dir_path, "system", "blockMeshDict")
    with open(bmd_file_path, "w") as f:
        f.write(str(block_mesh_dict))

    return{'FINISHED'}

def run_blockmesh(self, context):
    scene = context.scene
    obj = context.active_object

    print("Start openfoam")
    case_dir = bpy.path.abspath(scene.case_dir_path)
    mr = FoamCmdRunner(cmd_name='blockMesh', case_dir=case_dir)

    for info in mr.run():
        self.report({'WARNING'}, info)

    if mr.run_status:
        self.report({'INFO'}, 'Blockmesh : SUCCESS')
    else:
        self.report({'INFO'}, 'Blockmesh : FAILED')

    return{'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class BlockMeshDictPanel(Panel):
    bl_idname = "of_bmd_panel"
    bl_label = "Block Mesh Dict"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "mesh_edit"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene

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
    unregister_classes(__name__)
    del_scene_attrs('block_mesh_panel.yaml')

if __name__ == "__main__":
    register()
