import bpy

class PIVOTMAPPER_PT_panel(bpy.types.Panel):
    bl_label = "Pivot HUAAAPEper"
    bl_idname = "PIVOTMAPPER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Pivot Mapper'   # ← здесь задаёте свою вкладку

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.prop_search(scn, "pivotmapper_armature", scn, "objects", text="Armature")
        layout.operator("pivotmapper.align", icon='CONSTRAINT_BONE')
