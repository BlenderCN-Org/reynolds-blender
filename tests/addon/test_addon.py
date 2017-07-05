import unittest

import reynolds_blender

class TestAddon(unittest.TestCase):
    def test_addon_installed_and_enabled(self):
        # test if addon got loaded correctly
        # every addon must provide the "bl_info" dict
        self.assertIsNotNone(reynolds_blender.bl_info)

# manually invoke the test
suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
unittest.TextTestRunner().run(suite)

