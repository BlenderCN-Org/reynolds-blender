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
from bpy.types import Panel

from progress_report import ProgressReport

# --------------
# python imports
# --------------
import os

# ------------------------
# reynolds blender imports
# ------------------------

from reynolds_blender.gui.attrs import set_scene_attrs, del_scene_attrs
from reynolds_blender.gui.register import register_classes, unregister_classes
from reynolds_blender.gui.custom_operator import create_custom_operators
from reynolds_blender.gui.renderer import ReynoldsGUIRenderer

# ----------------
# reynolds imports
# ----------------

from reynolds.foam.cmd_runner import FoamCmdRunner

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

def solve_case(self, context):
    scene = context.scene
    obj = context.active_object

    # -------------------------
    # Start the console operatorr
    # --------------------------
    bpy.ops.reynolds.of_console_op()

    # ----------------------------------
    # Reset the status of a previous run
    # ----------------------------------
    case_dir = bpy.path.abspath(scene.case_dir_path)

    if case_dir is None or case_dir == '':
        self.report({'ERROR'}, 'Please select a case directory')
        return {'FINISHED'}

    if not scene.foam_started:
        self.report({'ERROR'}, 'Please start open foam')
        return {'FINISHED'}

    if not scene.blockmesh_executed:
        self.report({'ERROR'}, 'Please run blockMesh')
        return {'FINISHED'}

    shmd_file_path = os.path.join(case_dir, "system", "snappyHexMeshDict")
    if os.path.exists(shmd_file_path) and not scene.snappyhexmesh_executed:
        self.report({'ERROR'}, 'Please run snappyHexMesh')
        return {'FINISHED'}

    if scene.solver_name is None or scene.solver_name == '':
        self.report({'ERROR'}, 'Please select a solver')
        return {'FINISHED'}

    scene.case_solved = False
    sr = FoamCmdRunner(cmd_name=scene.solver_name,
                        case_dir=case_dir)
    for info in sr.run():
        self.report({'WARNING'}, info)

    if sr.run_status:
        scene.case_solved = True
        self.report({'INFO'}, 'Case solving: SUCCESS')
    else:
        scene.case_solved = False
        self.report({'INFO'}, 'Case solving: FAILED')

    return{'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class SolverPanel(Panel):
    bl_idname = "of_solver_panel"
    bl_label = "Solver"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ---------------------------------------
        # Render Solver Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout, 'solver_panel.yaml')
        gui_renderer.render()

def register():
    register_classes(__name__)
    create_custom_operators('solver_panel.yaml', __name__)

def unregister():
    unregister_classes(__name__)
# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------


if __name__ == '__main__':
    register()
