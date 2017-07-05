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

bl_info = {
    "name": "OpenFoam Add-On",
    "description": "",
    "author": "Deepak Surti",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

if "bpy" in locals():
    import importlib
    importlib.reload(foam)
    importlib.reload(block_mesh)
    importlib.reload(solver)
else:
    from . import foam, block_mesh, solver

import bpy

from bpy.props import (StringProperty,
                       PointerProperty)

def register():
    foam.register()
    block_mesh.register()
    solver.register()
    bpy.types.Scene.case_info_tool = PointerProperty(type=foam.CaseSettings)

def unregister():
    foam.unregister()
    block_mesh.unregister()
    solver.unregister()
    del bpy.types.Scene.case_info_tool

if __name__ == '__main__':
    register()
