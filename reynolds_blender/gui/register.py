import sys, inspect

import bpy

def get_module_class_members(module_name):
    return [cls_member for cls_member in
            inspect.getmembers(sys.modules[module_name], inspect.isclass)
            if getattr(cls_member[1], '__module__', None) == module_name]

def register_classes(module_name):
    for name, cls_member in get_module_class_members(module_name):
        print('Registering ', name)
        bpy.utils.register_class(cls_member)

def unregister_classes(module_name):
    for name, cls_member in get_module_class_members(module_name):
        print('Registering ', name)
        bpy.utils.unregister_class(cls_member)
