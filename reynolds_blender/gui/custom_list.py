import bpy

from bpy.props import IntProperty
from bpy.types import PropertyGroup, UIList

from .register import register_classes

#---------------
# custom UI list 
#---------------

def create_custom_list_operator(class_name, id_name, label,
                                data_prop, id_prop):
    list_actions = bpy.props.EnumProperty(
            items=(
                ('UP', "Up", ""),
                ('DOWN', "Down", ""),
                ('REMOVE', "Remove", ""),
                ('ADD', "Add", ""),
            )
        )

    def execute_func(self, context):
        return self.invoke(context, None)

    def invoke_func(self, context, event):
        scn = context.scene

        item_coll = getattr(scn, data_prop)
        item_idx = getattr(scn, id_prop)

        try:
            item = item_coll[item_idx]
        except IndexError:
            pass

        if self.action == 'REMOVE':
            item = item_coll[item_idx]
            info = 'Item %s removed from list' % (item.name)
            setattr(scn, id_prop, item_idx - 1)
            self.report({'INFO'}, info)
            item_coll.remove(item_idx)

        if self.action == 'ADD':
            item = item_coll.add()
            item.id = len(item_coll)
            setattr(scn, id_prop, len(item_coll) - 1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}

    opclass = type(class_name, (bpy.types.Operator, ),
                   {"bl_idname": id_name, "bl_label": label,
                    "execute": execute_func, "invoke": invoke_func,
                    "action": list_actions})

    print('Registering ', class_name, ' in module',
          getattr(opclass, '__module__', None))
    bpy.utils.register_class(opclass)

# --------------------------------------------
# custom rendering of each item in the list UI
# --------------------------------------------

class ReynoldsListItems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        split = layout.split(0.3)
        split.label("%d" % (index))
        split.prop(item, "name", text="", emboss=False, translate=False,
                   icon='BORDER_RECT')

    def invoke(self, context, event):
        pass

# -----------------------------------------------
# custom property group for list collection index
# -----------------------------------------------

class ReynoldsListLabel(bpy.types.PropertyGroup):
    id = IntProperty()

# ---------------------------------------------------------------------
# Register the classes for loading UI scene attrs and rendering UI list
# ---------------------------------------------------------------------
register_classes(__name__)
