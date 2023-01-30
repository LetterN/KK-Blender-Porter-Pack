import bpy

class update_bones(bpy.types.Operator):
    bl_idname = "kkb.finalizematerials"
    bl_label = "Finalize KKBP Materials"
    bl_description = "Bakes each material, then replaces the KKBP node groups with the baked material. A backup of the material with the KKBP nodes is saved as 'material_name-ORG'"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #bake the light and dark versions of each material
        bpy.context.scene.kkbp.bake_dark_bool = True
        bpy.context.scene.kkbp.bake_light_bool = True
        bpy.context.scene.kkbp.bake_norm_bool = False
        bpy.ops.kkb.bakematerials('INVOKE_DEFAULT')

        

        rigify_armature = [ob for ob in bpy.data.objects if ob.type == 'ARMATURE' and ob.get('rig_ui')]
        arm = rigify_armature[0] if len(rigify_armature) else bpy.data.objects['Armature']
        arm = bpy.data.armatures[arm.data.name]

        #check if the outfit linked to accessory bones on the armature is visible or not, then update the bone visibility
        for bone in arm.bones:
            if bone.get('KKBP outfit ID'):
                outfit_detected = False
                print("{} for {}".format(bone.name, bone['KKBP outfit ID']))
                for outfit_number in bone['KKBP outfit ID']:
                    matching_outfit = bpy.data.objects.get('Outfit 0' + str(outfit_number))
                    if matching_outfit:
                        print(matching_outfit.hide)
                        outfit_detected += not matching_outfit.hide
                bone.hide = False if outfit_detected else True

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(update_bones)