import bpy

bl_info = {
    "name": "Delete Keyframes Distance (DKD) - Pose",
    "author": "Ruslan Haru",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "Pose Mode > Sidebar > DKD > Delete Keyframes Distance (DKD) - Pose",
    "description": "Delete keyframes that are within or equal to the specified distance",
    "category": "Animation",
}

class DeleteKeyframesOperator(bpy.types.Operator):
    """Delete keyframes that are within or equal to the specified distance"""
    bl_idname = "pose.delete_keyframes_unique_id"
    bl_label = "Delete Keyframes Distance (DKD) - Pose"
    bl_description = "Delete keyframes that are within or equal to the specified distance"

    distance: bpy.props.IntProperty(name="Distance", default=5, min=1)
    delete_only_selected: bpy.props.BoolProperty(name="Delete Only Selected", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone is not None

    def execute(self, context):
        self.distance = context.scene.delete_keyframes_distance
        selected_bones = context.selected_pose_bones

        if not selected_bones:
            self.report({'ERROR'}, "No bones selected")
            return {'CANCELLED'}

        for pose_bone in selected_bones:
            action = pose_bone.id_data.animation_data.action
            if action is not None:
                fcurves_to_remove = []
                for fcurve in action.fcurves:
                    if fcurve.group.name.startswith(pose_bone.bone.name):
                        keyframes_to_remove = []
                        for keyframe_point in fcurve.keyframe_points:
                            current_frame = keyframe_point.co[0]
                            if self.delete_only_selected and not keyframe_point.select_control_point:
                                continue
                            if context.scene.delete_only_selected and not keyframe_point.select_control_point:
                                continue
                            keyframes_to_remove.append(keyframe_point)
                        for keyframe_point in keyframes_to_remove:
                            try:
                                fcurve.keyframe_points.remove(keyframe_point)
                            except RuntimeError:
                                pass
                self.report({'INFO'}, f"Keyframes within or equal to distance {self.distance} frames have been deleted for selected bones")
            else:
                self.report({'ERROR'}, "Selected bone has no animation data")
        return {'FINISHED'}

class DeleteKeyframesPanel(bpy.types.Panel):
    bl_label = "Delete Keyframes Distance (DKD) - Pose"
    bl_idname = "PT_DeleteKeyframesPanel_unique_id"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DKD Pose'
    bl_context = "posemode"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "delete_keyframes_distance", text="Distance")
        layout.prop(context.scene, "delete_only_selected", text="Delete Only Selected")
        layout.operator("pose.delete_keyframes_unique_id", text="Delete Keyframes")

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
