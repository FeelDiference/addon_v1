bl_info = {
    "name": "Pivot→Bone Mapper",
    "author": "Ваше Имя",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D › Sidebar › Pivot Mapper",
    "description": "Выравнивает Origin мешей по головам костей",
    "category": "Object",
}

from .operators import PIVOTMAPPER_OT_align
from .panel     import PIVOTMAPPER_PT_panel

def register():
    import bpy
    bpy.types.Scene.pivotmapper_armature = bpy.props.StringProperty(
        name="Armature Object",
        description="Имя Armature для выравнивания Origin"
    )
    bpy.utils.register_class(PIVOTMAPPER_OT_align)
    bpy.utils.register_class(PIVOTMAPPER_PT_panel)

def unregister():
    import bpy
    del bpy.types.Scene.pivotmapper_armature
    bpy.utils.unregister_class(PIVOTMAPPER_PT_panel)
    bpy.utils.unregister_class(PIVOTMAPPER_OT_align)
