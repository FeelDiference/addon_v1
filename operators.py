import bpy

class PIVOTMAPPER_OT_align(bpy.types.Operator):
    bl_idname = "pivotmapper.align"
    bl_label = "Align Pivots to Bones"
    bl_description = "Перемещает только Origin мешей к головам костей по именам до точки «.»"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        arm = scene.objects.get(scene.pivotmapper_armature)
        if not arm or arm.type != 'ARMATURE':
            self.report({'ERROR'}, "Укажите корректную Armature в настройках аддона")
            return {'CANCELLED'}

        # Сохраним текущую позицию 3D‑курсоpа, чтобы вернуть её потом
        prev_cursor_loc = scene.cursor.location.copy()

        # Будем переключаться по мешам в сцене
        for obj in scene.objects:
            if obj.type != 'MESH':
                continue

            # Берём имя до первой точки
            base_name = obj.name.split('.', 1)[0]
            bone = arm.data.bones.get(base_name)
            if not bone:
                continue

            # Мировая позиция головы кости
            world_head = arm.matrix_world @ bone.head_local

            # Переместим 3D-курсор в эту точку
            scene.cursor.location = world_head

            # Активируем только этот объект и вызываем origin_set
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            # теперь Origin объекта установлен в точке world_head, сам объект не двинулся

        # Вернём 3D‑курсор на место
        scene.cursor.location = prev_cursor_loc

        # Можно вернуть выделение на всё, если нужно
        # bpy.ops.object.select_all(action='SELECT')

        return {'FINISHED'}
