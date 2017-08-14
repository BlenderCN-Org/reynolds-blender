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

# ------------------------
# reynolds blender imports
# ------------------------

from reynolds_blender.gui.register import register_classes, unregister_classes
from reynolds_blender.gui.renderer import ReynoldsGUIRenderer
from reynolds_blender.gui.custom_operator import create_custom_operators

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

    # ----------------------------------
    # Reset the status of a previous run
    # ----------------------------------
    scene.case_solved = False
    case_dir = bpy.path.abspath(scene.case_dir_path)
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

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ---------------------------------------
        # Render Solver Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout, 'solver_panel.yaml')
        gui_renderer.render()

def register():
    create_custom_operators('solver_panel.yaml', __name__)
    register_classes(__name__)

def unregister():
    unregister_classes(__name__)
# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------


if __name__ == '__main__':
    register()
