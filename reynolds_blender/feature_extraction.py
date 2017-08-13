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

def mark_location_in_mesh(self, context):
    scene = context.scene
    print(scene.cursor_location)
    scene.location_in_mesh = scene.cursor_location
    print(' set loc in mesh ', scene.location_in_mesh)
    return {'FINISHED'}

def show_location_in_mesh(self, context):
    scene = context.scene
    print(' move cursor to loc in mesh ', scene.location_in_mesh)
    scene.cursor_location = scene.location_in_mesh
    return {'FINISHED'}

def generate_surface_dict(self, context):
    scene = context.scene
    surface_feature_dict = ReynoldsFoamDict('surfaceFeatureExtractDict.foam')

    for name, geometry_info in scene.geometries.items():
        if geometry_info['has_features']:
            print('generate feature extract dict for ', name)
            file_path = geometry_info.get('file_path', None)
            if file_path:
                key = os.path.basename(file_path)
            else:
                key = name
            surface_feature_dict[key] = {}
            surface_feature_dict[key]['extractionMethod'] = 'extractFromSurface'
            surface_feature_dict[key]['writeObj'] = 'no'
            coeffs = {'includedAngle': geometry_info['included_angle']}
            surface_feature_dict[key]['extractFromSurfaceCoeffs'] = coeffs
            print(surface_feature_dict[key])

    print(surface_feature_dict)
    abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
    sfed_file_path = os.path.join(abs_case_dir_path, "system",
                                  "surfaceFeatureExtractDict")
    with open(sfed_file_path, "w") as f:
        f.write(str(surface_feature_dict))

    return {'FINISHED'}

def extract_surface_features(self, context):
    print('extract surface features: TBD')

    return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class FeatureExtractionPanel(Panel):
    bl_idname = "of_feature_extract_panel"
    bl_label = "Surface Feature Extraction"
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
        # Render Block Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'feature_extraction.yaml')
        gui_renderer.render()


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('feature_extraction.yaml')
    create_custom_operators('feature_extraction.yaml', __name__)

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('feature_extraction.yaml')

if __name__ == "__main__":
    register()
