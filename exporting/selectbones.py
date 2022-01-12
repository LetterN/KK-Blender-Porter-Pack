'''
SELECT BONES SCRIPT
- Selects bones that aren't needed. This is useful for reducing the bone count with the "Merge Weights" option in CATS

Usage:
- Make sure all the hair / accessory bones you want to keep are visible in pose mode
- Run the script
- Use the "Merge Weights to Parent" option in CATS (under Model Options)
'''

import bpy
from ..importing.finalizepmx import kklog

class select_bones(bpy.types.Operator):
    bl_idname = "kkb.selectbones"
    bl_label = "Prep for target application"
    bl_description = "Check the dropdown for more info"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene.placeholder
        prep_type = scene.prep_dropdown

        kklog('\nPrepping for export...')
        #Combine all objects
        kklog('\nCombining all objects...')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active=bpy.data.objects['Body']
        body = bpy.context.view_layer.objects.active
        bpy.ops.object.join()
        
        kklog('\nRemoving object outline modifier...')
        body.modifiers['Outline Modifier'].show_render = False
        body.modifiers['Outline Modifier'].show_viewport = False

        #remove the second Template Eye slot if there are two of the same name in a row
        kklog('\nRemoving duplicate Eye materials...')
        eye_index = 0
        for mat_slot_index in range(len(body.material_slots)):
            if body.material_slots[mat_slot_index].name == 'Template Eye (hitomi)':
                index = mat_slot_index
        if body.material_slots[index].name == body.material_slots[index-1].name:
            body.active_material_index = index
            bpy.ops.object.material_slot_remove()

        #Select the armature and make it active
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Armature'].hide_set(False)
        bpy.data.objects['Armature'].select_set(True)
        bpy.context.view_layer.objects.active=bpy.data.objects['Armature']
        bpy.ops.object.mode_set(mode='POSE')

        #If simplifying the bones...
        if prep_type in ['A', 'B']:
            #show all bones on the armature
            allLayers = [True, True, True, True, True, True, True, True,
                        True, True, True, True, True, True, True, True,
                        True, True, True, True, True, True, True, True,
                        True, True, True, True, True, True, True, True]
            bpy.data.objects['Armature'].data.layers = allLayers
            bpy.ops.pose.select_all(action='DESELECT')

            #Select bones on layer 11
            armature = bpy.data.objects['Armature']
            for bone in armature.data.bones:
                if bone.layers[10]==True:
                    bone.select = True
            
            kklog('Using CATS to simplify bones...')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.cats_manual.merge_weights()

        #If exporting for VRM...
        if prep_type == 'A':
            
            '''
            #remove materials and shapekeys
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active=body
            for x in body.material_slots:
                body.active_material_index = 0
                bpy.ops.object.material_slot_remove()
            
            bpy.ops.object.shape_key_remove(all=True)
            '''

            bpy.context.view_layer.objects.active=armature
            bpy.ops.object.mode_set(mode='EDIT')

            #Rearrange bones to match CATS output 
            armature.data.edit_bones['Pelvis'].parent = None
            armature.data.edit_bones['Spine'].parent = armature.data.edit_bones['Pelvis']
            armature.data.edit_bones['Hips'].name = 'dont need lol'
            armature.data.edit_bones['Pelvis'].name = 'Hips'
            armature.data.edit_bones['Left leg'].parent = armature.data.edit_bones['Hips']
            armature.data.edit_bones['Right leg'].parent = armature.data.edit_bones['Hips']
            armature.data.edit_bones['Left ankle'].parent = armature.data.edit_bones['Left knee']
            armature.data.edit_bones['Right ankle'].parent = armature.data.edit_bones['Right knee']
            armature.data.edit_bones['Left shoulder'].parent = armature.data.edit_bones['Upper Chest']
            armature.data.edit_bones['Right shoulder'].parent = armature.data.edit_bones['Upper Chest']

            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')

            #Select bones on layer 3/5/12/13
            armature = bpy.data.objects['Armature']
            merge_these = ['cf_j_waist02', 'cf_s_waist01', 'cf_s_hand_L', 'cf_s_hand_R']
            for bone in armature.data.bones:
                if bone.layers[11]==True or bone.layers[12] == True or bone.layers[2] == True or bone.layers[4] == True:
                    bone.select = True
                if bone.name in merge_these:
                    bone.select = True
            
            kklog('Using CATS to simplify more bones...')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.cats_manual.merge_weights()

        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    

if __name__ == "__main__":
    bpy.utils.register_class(select_bones)

    # test call
    print((bpy.ops.kkb.selectbones('INVOKE_DEFAULT')))