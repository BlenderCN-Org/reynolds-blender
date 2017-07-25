import bpy

import json
import os

from .register import register_classes

class ReynoldsGUIRenderer(object):
    def __init__(self, scene, layout, gui_filename):
        self.scene = scene
        self.layout = layout

        current_dir = os.path.realpath(os.path.dirname(__file__))
        gui_file = os.path.join(current_dir, "../json", "panels", gui_filename)

        print('Reading GUI Spec from : ', gui_file)

        self.gui_spec = {}
        with open(gui_file) as f:
            self.gui_spec = json.load(f)

    def render(self):
        for gui_element in self.gui_spec['gui_elements']:
            self._render_gui_element(gui_element, self.layout)

    def _render_gui_element(self, gui_element, parent):
        name = list(gui_element.keys())[0]
        metadata = gui_element[name]

        print('Rendering element: ', name, metadata)

        if name == 'box':
            box = parent.box()
            for child in metadata:
                self._render_gui_element(child, box)

        if name == 'label':
            label = parent.label(text=metadata.get('text', ''))

        if name == 'row':
            row = parent.row()
            for child in metadata:
                self._render_gui_element(child, row)

        if name == 'prop':
            parent.prop(self.scene, metadata['scene_attr'])

        if name == 'operator':
            parent.operator(metadata['id'], icon=metadata['icon'])

        if name == 'separator':
            for i in range(metadata['nums']):
                parent.separator()

