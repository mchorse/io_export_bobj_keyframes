bl_info = {
    "name": "BOBJ keyframes",
    "author": "McHorse",
    "version": (0, 1, 0),
    "blender": (2, 77, 0),
    "location": "File > Export",
    "description": "Export actions (animation keyframes) into .bobj file",
    "warning": "",
    "category": "Export"
}

import bpy
from bpy.props import (BoolProperty, FloatProperty, StringProperty, EnumProperty)
from bpy_extras.io_utils import (ExportHelper, orientation_helper_factory, path_reference_mode, axis_conversion)

IOOBJOrientationHelper = orientation_helper_factory("IOOBJOrientationHelper", axis_forward='Z', axis_up='Y')

# Export panel
class ExportOBJ(bpy.types.Operator, ExportHelper, IOOBJOrientationHelper):
    # Panel's information
    bl_idname = "export_scene.bobj_keyframes"
    bl_label = 'Export BOBJ keyframes'
    bl_options = {'PRESET'}

    # Panel's properties
    filename_ext = ".bobj"
    filter_glob = StringProperty(default="*.bobj", options={'HIDDEN'})
    path_mode = path_reference_mode
    check_extension = True

    def execute(self, context):
        from . import export_bobj
        from mathutils import Matrix
        
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "check_existing", "filter_glob", "path_mode"))
        
        return export_bobj.save(context, **keywords)

# Register and stuff
def menu_func_export(self, context):
    self.layout.operator(ExportOBJ.bl_idname, text="BOBJ keyframes (.bobj)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)