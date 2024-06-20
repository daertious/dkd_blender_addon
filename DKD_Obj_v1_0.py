import bpy

bl_info = {
    "name": "Delete Keyframes Distance (DKD) - Obj",
    "author": "Ruslan Haru",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > DKD > Delete Keyframes Distance (DKD) - Obj",
    "description": "Delete keyframes that are within or equal to the specified distance",
    "category": "Animation",
}

class DeleteKeyframesOperator(bpy.types.Operator):
    """Delete keyframes that are within or equal to the specified distance"""
    bl_idname = "object.delete_keyframes"
    bl_label = "Delete Keyframes Distance (DKD) - Obj"
    bl_description = "Delete keyframes that are within or equal to the specified distance"

    distance: bpy.props.IntProperty(name="Distance", default=5, min=1)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.animation_data is not None

    def execute(self, context):
        self.distance = context.scene.delete_keyframes_distance
        obj = context.active_object
        anim_data = obj.animation_data
        if anim_data is not None and anim_data.action is not None:
            action = anim_data.action
            fcurves_to_remove = []
            for fcurve in action.fcurves:
                keyframes_to_remove = []
                for i in range(len(fcurve.keyframe_points) - 1):
                    current_frame = fcurve.keyframe_points[i].co[0]
                    next_frame = fcurve.keyframe_points[i + 1].co[0]
                    if next_frame - current_frame <= self.distance:
                        if context.scene.delete_only_selected:
                            if fcurve.keyframe_points[i].select_control_point:
                                keyframes_to_remove.append(i + 1)
                        else:
                            keyframes_to_remove.append(i + 1)
                for index in reversed(keyframes_to_remove):
                    fcurve.keyframe_points.remove(fcurve.keyframe_points[index])
            self.report({'INFO'}, f"Keyframes within or equal to distance {self.distance} frames have been deleted")
        else:
            self.report({'ERROR'}, "Object has no animation data")
        return {'FINISHED'}

class DeleteKeyframesPanel(bpy.types.Panel):
    bl_label = "Delete Keyframes Distance (DKD) - Obj"
    bl_idname = "PT_DeleteKeyframesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DKD Obj'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "delete_keyframes_distance", text="Distance")
        layout.prop(context.scene, "delete_only_selected", text="Delete Only Selected")
        layout.operator("object.delete_keyframes", text="Delete Keyframes")

classes = (
    DeleteKeyframesOperator,
    DeleteKeyframesPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.delete_keyframes_distance = bpy.props.IntProperty(name="Distance", default=5, min=1)
    bpy.types.Scene.delete_only_selected = bpy.props.BoolProperty(name="Delete Only Selected", default=False)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.delete_keyframes_distance
    del bpy.types.Scene.delete_only_selected

if __name__ == "__main__":
    register()
