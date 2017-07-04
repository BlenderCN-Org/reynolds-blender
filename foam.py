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
import bpy
from bpy.types import (Panel,
                       PropertyGroup)
from bpy.props import StringProperty

# ---------------
# reynolds imports
# ----------------
from reynolds.foam.start import FoamRunner

class CaseSettings(PropertyGroup):
    case_dir_path = StringProperty(
        name="",
        description="Choose a directory:",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

class BMDStartOpenFoamOperator(bpy.types.Operator):
    bl_idname = "reynolds.start_of"
    bl_label = "Start OpenFoam"

    def execute(self, context):
        scene = context.scene
        bmd_tool = scene.bmd_tool
        obj = context.active_object

        print("Start openfoam")

        fr = FoamRunner()
        status = fr.start()
        if status:
            print("OpenFoam started: SUCCESS")
        else:
            print("OpenFoam started: FAILURE")

        return{'FINISHED'}

class FoamPanel(Panel):
    bl_idname = "of_foam_panel"
    bl_label = "Open Foam"
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
        case_info_tool = scene.case_info_tool

        # --------------
        # Foam Panel
        # --------------

        rbox = layout.box()
        rbox.label(text="Case Dir")
        rbrow = rbox.row()
        rbrow.prop(case_info_tool, "case_dir_path")
        rbrow = rbox.row()
        rbrow.operator("reynolds.start_of", icon="VERTEXSEL")

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_class(BMDStartOpenFoamOperator)
    bpy.utils.register_class(FoamPanel)
    bpy.utils.register_class(CaseSettings)

def unregister():
    bpy.utils.unregister_class(BMDStartOpenFoamOperator)
    bpy.utils.unregister_class(FoamPanel)
    bpy.utils.unregister_class(CaseSettings)

if __name__ == '__main__':
    register()
