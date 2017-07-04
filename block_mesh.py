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

# ----------------
# reynolds imports
# ----------------
from reynolds.blockmesh.mesh_components import Vertex3, Block, SimpleGrading, Face, BoundaryRegion
from reynolds.blockmesh.mesh_dict import MeshDict
from reynolds.blockmesh.mesh_runner import MeshRunner
from reynolds.solver.solver_runner import SolverRunner

# ------------------------------------------------------------------------
#    custom UI list for adding vertices
# ------------------------------------------------------------------------

class VerticesListActions(bpy.types.Operator):
    bl_idname = "vertices.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.bmd_vindex

        try:
            item = scn.bmd_vertices[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(scn.bmd_vertices) - 1:
                item_next = scn.bmd_vertices[idx+1].name
                scn.bmd_vindex += 1
                info = 'Item %d selected' % (scn.bmd_vindex + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.bmd_vertices[idx-1].name
                scn.bmd_vindex -= 1
                info = 'Item %d selected' % (scn.bmd_vindex - 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                item = scn.bmd_vertices[scn.bmd_vindex]
                info = 'Item %s removed from list' % (item.name)
                scn.bmd_vindex -= 1
                self.report({'INFO'}, info)
                scn.bmd_vertices.remove(idx)
                if item.name != "":
                    _, v_index = item.name.split("Vertex ", 1)
                    if v_index in scn.vertex_labels:
                        scn.vertex_labels.pop(v_index)

        if self.action == 'ADD':
            item = scn.bmd_vertices.add()
            item.id = len(scn.bmd_vertices)
            scn.bmd_vindex = (len(scn.bmd_vertices)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}

class VerticesItems(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.label("Label: %d" % (index))
        split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass

# Create custom property group
class BMDVertexLabel(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    id = IntProperty()

# ------------------------------------------------------------------------
#    custom UI list for adding regions
# ------------------------------------------------------------------------

class RegionsListActions(bpy.types.Operator):
    bl_idname = "regions.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.bmd_rindex

        try:
            item = scn.bmd_regions[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(scn.bmd_regions) - 1:
                item_next = scn.bmd_regions[idx+1].name
                scn.bmd_rindex += 1
                info = 'Item %d selected' % (scn.bmd_rindex + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.bmd_regions[idx-1].name
                scn.bmd_rindex -= 1
                info = 'Item %d selected' % (scn.bmd_rindex - 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                item = scn.bmd_regions[scn.bmd_rindex]
                info = 'Item %s removed from list' % (item.name)
                scn.bmd_rindex -= 1
                self.report({'INFO'}, info)
                scn.bmd_regions.remove(idx)


        if self.action == 'ADD':
            item = scn.bmd_regions.add()
            item.id = len(scn.bmd_regions)
            scn.bmd_rindex = (len(scn.bmd_regions)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}

class RegionsItems(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.label("Region : ")
        split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass

# Create custom property group
class BMDRegionLabel(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    id = IntProperty()

    region_type = EnumProperty(
        name="Type:",
        description="Patch/Region Type.",
        items=[ ('empty', "empty", ""),
                ('wall', "wall", ""),
               ]
        )

    region_name = StringProperty(
        name="Patch/Region Name",
        description=":",
        default="",
        maxlen=1024,
        )

# ------------------------------------------------------------------------
#    store properties in the active scene
# ------------------------------------------------------------------------

class BlockMeshDictSettings(PropertyGroup):
    convert_to_meters = FloatProperty(
        name = "Convert to meters",
        description="Scaling factor by which all vertex coordinates are multiplied.",
        default=0.001)

    n_cells = IntVectorProperty(
        name = "Cells",
        description = "Number of cells in XYZ axis direction",
        default=(1, 1, 1),
        subtype="XYZ")

    n_grading = IntVectorProperty(
        name = "Cell expansion ratios",
        description = "Cell expansion ratios",
        default=(1, 1, 1),
        subtype="XYZ")

    region_name = StringProperty(
        name="Patch/Region Name",
        description=":",
        default="",
        maxlen=1024,
        )

    region_type = EnumProperty(
        name="Type:",
        description="Patch/Region Type.",
        items=[ ('empty', "empty", ""),
                ('wall', "wall", ""),
               ]
        )

    solver_name = StringProperty(
        name="Solver Name",
        description=":",
        default="",
        maxlen=1024,
        )

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

class BMDVerticesOperator(bpy.types.Operator):
    bl_idname = "reynolds.vertices"
    bl_label = "Assign Vertices"

    def execute(self, context):
        scene = context.scene
        mytool = scene.bmd_tool

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
        bmd_tool = scene.bmd_tool
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
        bmd_tool = scene.bmd_tool

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
        region_name = scene.bmd_tool.region_name
        face_str = region_name + " : " + ' '.join(str(f) for f in r_faces)
        r = (scene.bmd_tool.region_name, scene.bmd_tool.region_type, r_faces)
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
        bmd_tool = scene.bmd_tool
        case_info_tool = scene.case_info_tool
        obj = context.active_object

        print("Select dir for generated blockmeshdict file")

        abs_case_dir_path = bpy.path.abspath(case_info_tool.case_dir_path)

        # generate bmd vertices
        bmd_vertices = []
        sorted_labels = sorted(scene.vertex_labels.items(), key=operator.itemgetter(1))
        for v_index, _ in sorted_labels:
            v = obj.data.vertices[v_index].co
            print(v)
            bmd_v = Vertex3(v.x, v.z, v.y) # Swap y, z
            bmd_vertices.append(bmd_v)

        # generate bmd blocks
        block_cells = bmd_tool.n_cells
        block_grading = bmd_tool.n_grading
        sg = SimpleGrading([block_grading[0], block_grading[1], block_grading[2]])
        bmd_block = Block(scene.blocks, [block_cells[0], block_cells[1], block_cells[2]], sg)
        print(bmd_block)

        # generate bmd regions
        bmd_regions = []
        for name, r in scene.regions.items():
            n, type, face_labels = r
            faces = []
            for f in face_labels:
                faces.append(Face(f))
            br = BoundaryRegion(n, type, faces)
            bmd_regions.append(br)

        bmd = MeshDict(bmd_tool.convert_to_meters, bmd_vertices, bmd_block, bmd_regions)

        print(bmd.dict_string())

        bmd_file_path = os.path.join(abs_case_dir_path, "system", "blockMeshDict")
        with open(bmd_file_path, "w") as f:
            f.write(bmd.dict_string())

        return{'FINISHED'}


class BMDSolveCaseOperator(bpy.types.Operator):
    bl_idname = "reynolds.solve_case"
    bl_label = "Solve OpenFoam Case"

    def execute(self, context):
        scene = context.scene
        bmd_tool = scene.bmd_tool
        case_info_tool = scene.case_info_tool
        obj = context.active_object

        print("Start openfoam")
        case_dir = bpy.path.abspath(case_info_tool.case_dir_path)
        mr = MeshRunner(case_dir=case_dir)
        status, out, err = mr.run()
        if status:
            print("blockMesh success")
            sr = SolverRunner(solver_name=bmd_tool.solver_name,
                              case_dir=case_dir)
            status, out, err = sr.run()
            if status:
                print("Case solved successfully")
            else:
                print("Case solving failed", out, err)
        else:
            print("BlockMesh failed", out, err)

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
        bmd_tool = scene.bmd_tool

        # --------------
        # Vertices Panel
        # --------------

        rbox = layout.box()
        rbox.label(text="Vertices")
        rbox.prop(bmd_tool, "convert_to_meters")
        rbrow = rbox.row()
        rbrow.template_list("VerticesItems", "", scene, "bmd_vertices", scene, "bmd_vindex", rows=2)

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
        bbox.prop(bmd_tool, "n_cells")
        bbox.prop(bmd_tool, "n_grading")
        bbox.operator("reynolds.blocks", icon="MESH_CUBE")

        # --------------
        # Regions Panel
        # --------------

        rbox = layout.box()
        rbox.label(text="Regions")
        rbrow = rbox.row()
        rbrow.template_list("RegionsItems", "", scene, "bmd_regions", scene, "bmd_rindex", rows=2)

        col = rbrow.column(align=True)
        col.operator("regions.list_action", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("regions.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()

        rbrow2 = rbox.row()
        rbrow2.prop(bmd_tool, "region_name")
        rbrow2.prop(bmd_tool, "region_type")
        rbrow2.separator()
        rbrow3 = rbox.row()
        rbrow3.operator("reynolds.assign_region", icon="VERTEXSEL")
        rbrow3.operator("reynolds.remove_region", icon="X")

        # -----------------------------
        # Generate blockmesh dict panel
        # -----------------------------

        rbox = layout.box()
        rbox.label(text="Case")
        rbrow2 = rbox.row()
        rbrow2.prop(bmd_tool, "solver_name")
        rbrow2.separator()
        rbrow3 = rbox.row()
        rbrow3.operator("reynolds.generate_bmd", icon="FILE_TEXT")
        rbrow3.operator("reynolds.solve_case", icon="IPO_BACK")

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VerticesListActions)
    bpy.utils.register_class(VerticesItems)
    bpy.utils.register_class(BMDVertexLabel)
    bpy.utils.register_class(RegionsListActions)
    bpy.utils.register_class(RegionsItems)
    bpy.utils.register_class(BMDRegionLabel)
    bpy.utils.register_class(BlockMeshDictSettings)
    bpy.utils.register_class(BMDVerticesOperator)
    bpy.utils.register_class(BMDBlocksOperator)
    bpy.utils.register_class(BMDVertexAssignOperator)
    bpy.utils.register_class(BMDVertexRemoveOperator)
    bpy.utils.register_class(BMDRegionsAssignOperator)
    bpy.utils.register_class(BMDRegionsRemoveOperator)
    bpy.utils.register_class(BMDGenerateDictOperator)
    bpy.utils.register_class(BMDSolveCaseOperator)
    bpy.utils.register_class(BlockMeshDictPanel)
    bpy.types.Scene.vertex_labels = {}
    bpy.types.Scene.blocks = []
    bpy.types.Scene.regions = {}
    bpy.types.Scene.bmd_vertices = CollectionProperty(type=BMDVertexLabel)
    bpy.types.Scene.bmd_vindex = IntProperty()
    bpy.types.Scene.bmd_regions = CollectionProperty(type=BMDRegionLabel)
    bpy.types.Scene.bmd_rindex = IntProperty()
    bpy.types.Scene.bmd_tool = PointerProperty(type=BlockMeshDictSettings)


def unregister():
    bpy.utils.unregister_class(VerticesListActions)
    bpy.utils.unregister_class(VerticesItems)
    bpy.utils.unregister_class(BMDVertexLabel)
    bpy.utils.unregister_class(RegionsListActions)
    bpy.utils.unregister_class(RegionsItems)
    bpy.utils.unregister_class(BMDRegionLabel)
    bpy.utils.unregister_class(BlockMeshDictSettings)
    bpy.utils.unregister_class(BMDVerticesOperator)
    bpy.utils.unregister_class(BMDBlocksOperator)
    bpy.utils.unregister_class(BMDVertexAssignOperator)
    bpy.utils.unregister_class(BMDVertexRemoveOperator)
    bpy.utils.unregister_class(BMDRegionsAssignOperator)
    bpy.utils.unregister_class(BMDRegionsRemoveOperator)
    bpy.utils.unregister_class(BMDGenerateDictOperator)
    bpy.utils.unregister_class(BMDSolveCaseOperator)
    bpy.utils.unregister_class(BlockMeshDictPanel)
    del bpy.types.Scene.vertex_labels
    del bpy.types.Scene.blocks
    del bpy.types.Scene.regions
    del bpy.types.Scene.bmd_vertices
    del bpy.types.Scene.bmd_vindex
    del bpy.types.Scene.bmd_regions
    del bpy.types.Scene.bmd_rindex
    del bpy.types.Scene.bmd_tool

if __name__ == "__main__":
    register()