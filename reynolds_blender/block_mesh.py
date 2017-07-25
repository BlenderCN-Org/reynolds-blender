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
from reynolds_blender.gui.custom_list import create_custom_list_operator

# ----------------
# reynolds imports
# ----------------
from reynolds.json.schema_gen import FoamDictJSONGenerator
from reynolds.dict.foam_dict_gen import FoamDictGenerator
from reynolds.foam.cmd_runner import FoamCmdRunner

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

class BMDVerticesOperator(bpy.types.Operator):
    bl_idname = "reynolds.vertices"
    bl_label = "Assign Vertices"

    def execute(self, context):
        scene = context.scene

        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)

        for f in bm.faces:
            if f.select:
                f_idx = f.index
                print("Selected face: ", f_idx)
                for v_idx in obj.data.polygons[f_idx].vertices:
                    x, y, z = obj.matrix_world * obj.data.vertices[v_idx].co
                    print(v_idx, ':', x, y, z)
                break

        for v in obj.data.vertices:
            x, y, z = v.co
            print(x, y, z)

        return {'FINISHED'}


class BMDBlocksOperator(bpy.types.Operator):
    bl_idname = "reynolds.blocks"
    bl_label = "Assign Blocks"

    def execute(self, context):
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

class BMDVertexAssignOperator(bpy.types.Operator):
    bl_idname = "reynolds.assign_vertex"
    bl_label = "Assign"
    bl_description = "Assign vertex to the label"

    def execute(self, context):
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


class BMDVertexRemoveOperator(bpy.types.Operator):
    bl_idname = "reynolds.remove_vertex"
    bl_label = "Remove"
    bl_description = "Remove assigned vertex"

    def execute(self, context):
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

class BMDRegionsAssignOperator(bpy.types.Operator):
    bl_idname = "reynolds.assign_region"
    bl_label = "Assign"
    bl_description = "Assign faces to the region"

    def execute(self, context):
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

class BMDRegionsRemoveOperator(bpy.types.Operator):
    bl_idname = "reynolds.remove_region"
    bl_label = "Remove"
    bl_description = "Remove faces assigned to the region"

    def execute(self, context):
        print("Removing region")

        scene = context.scene
        obj = context.active_object

        print(scene.bmd_rindex, scene.bmd_regions[scene.bmd_rindex])
        item = scene.bmd_regions[scene.bmd_rindex]
        r_name, _ = item.name.split(" : ", 1)
        scene.regions.pop(r_name, None)
        item.name = ""
        return{'FINISHED'}

class BMDGenerateDictOperator(bpy.types.Operator):
    bl_idname = "reynolds.generate_bmd"
    bl_label = "Generate Block Mesh Dict"

    def execute(self, context):
        scene = context.scene
        obj = context.active_object

        print("Select dir for generated blockmeshdict file")

        abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)

        # generate bmd vertices
        bmd_vertices = []
        sorted_labels = sorted(scene.vertex_labels.items(), key=operator.itemgetter(1))
        for v_index, _ in sorted_labels:
            v = obj.data.vertices[v_index].co
            print(v)
            bmd_v = [v.x, v.z, v.y] # Swap y, z
            bmd_vertices.append(bmd_v)

        # generate bmd blocks
        bmd_blocks_dict = {}
        bmd_blocks_dict['vertex_nums'] = scene.blocks
        block_cells = scene.n_cells
        bmd_blocks_dict['num_cells'] = [block_cells[0],
                                        block_cells[1],
                                        block_cells[2]]
        bmd_blocks_dict['grading'] = 'simpleGrading'
        block_grading = scene.n_grading
        bmd_blocks_dict['grading_x'] = [[1, 1, block_grading[0]]]
        bmd_blocks_dict['grading_y'] = [[1, 1, block_grading[1]]]
        bmd_blocks_dict['grading_z'] = [[1, 1, block_grading[2]]]
        print(bmd_blocks_dict)

        # generate bmd regions
        bmd_regions = []
        for name, r in scene.regions.items():
            br = {}
            n, type, face_labels = r
            br['name'] = n
            br['type'] = type
            faces = []
            for f in face_labels:
                faces.append(f)
            br['faces'] = faces
            bmd_regions.append(br)
        print(bmd_regions)

        block_mesh_dict_gen = FoamDictJSONGenerator('blockMeshDict.schema')
        block_mesh_dict_json = block_mesh_dict_gen.json_obj

         # set header info
        block_mesh_dict_json['version'] = '2.0'
        block_mesh_dict_json['format'] = 'ascii'
        block_mesh_dict_json['class'] = 'dictionary'
        block_mesh_dict_json['object'] = 'blockMeshDict'

        # set convert to meters
        block_mesh_dict_json['convertToMeters'] = scene.convert_to_meters

        # set vertices
        print(bmd_vertices)
        block_mesh_dict_json['vertices'] = bmd_vertices

        # set blocks
        block_mesh_dict_json['blocks'] = bmd_blocks_dict

        # set boundary
        block_mesh_dict_json['boundary'] = bmd_regions

        # generate the blockMeshDict
        foam_dict_gen = FoamDictGenerator(block_mesh_dict_json,
                                          'blockMeshDict.foam')
        block_mesh_dict = foam_dict_gen.foam_dict

        # bmd = MeshDict(scene.convert_to_meters, bmd_vertices, bmd_block, bmd_regions)

        print(block_mesh_dict)

        bmd_file_path = os.path.join(abs_case_dir_path, "system", "blockMeshDict")
        with open(bmd_file_path, "w") as f:
            f.write(block_mesh_dict)

        return{'FINISHED'}


class BMDBlockMeshRunnerOperator(bpy.types.Operator):
    bl_idname = "reynolds.block_mesh_runner"
    bl_label = "Run blockMesh"

    def execute(self, context):
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
#    block mesh dict tool in edit mode
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

        # --------------
        # Vertices Panel
        # --------------

        rbox = layout.box()
        rbox.label(text="Vertices")
        rbox.prop(scene, "convert_to_meters")
        rbrow = rbox.row()
        rbrow.template_list("ReynoldsListItems", "", scene, "bmd_vertices", scene, "bmd_vindex", rows=2)

        col = rbrow.column(align=True)
        col.operator("vertices.list_action", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("vertices.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()

        rbrow2 = rbox.row()
        rbrow2.operator("reynolds.assign_vertex", icon="VERTEXSEL")
        rbrow2.operator("reynolds.remove_vertex", icon="X")
        rbrow2.separator()

        # ------------
        # Blocks Panel
        # ------------

        bbox = layout.box()
        bbox.label(text="Blocks")
        bbox.prop(scene, "n_cells")
        bbox.prop(scene, "n_grading")
        bbox.operator("reynolds.blocks", icon="MESH_CUBE")

        # --------------
        # Regions Panel
        # --------------

        rbox = layout.box()
        rbox.label(text="Regions")
        rbrow = rbox.row()
        rbrow.template_list("ReynoldsListItems", "", scene, "bmd_regions", scene, "bmd_rindex", rows=2)

        col = rbrow.column(align=True)
        col.operator("regions.list_action", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("regions.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()

        rbrow2 = rbox.row()
        rbrow2.prop(scene, "region_name")
        rbrow2.prop(scene, "region_type")
        rbrow2.separator()
        rbrow3 = rbox.row()
        rbrow3.operator("reynolds.assign_region", icon="VERTEXSEL")
        rbrow3.operator("reynolds.remove_region", icon="X")

        # -----------------------------
        # Generate blockmesh dict panel
        # -----------------------------

        rbox = layout.box()
        rbox.label(text="BlockMesh")
        rbrow3 = rbox.row()
        rbrow3.operator("reynolds.generate_bmd", icon="FILE_TEXT")
        rbrow3.operator("reynolds.block_mesh_runner", icon="FILE_TEXT")

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('block_mesh_attrs.json')
    create_custom_list_operator('VerticesListActions', 
                                'vertices.list_action', 'Vertices List',
                                'bmd_vertices', 'bmd_vindex')
    create_custom_list_operator('RegionsListActions',
                                'regions.list_action', 'Regions List',
                                'bmd_regions', 'bmd_rindex')

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('block_mesh_attrs.json')

if __name__ == "__main__":
    register()
