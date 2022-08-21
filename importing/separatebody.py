import bpy, json, time, traceback
from .importbuttons import kklog
from ..extras.linkshapekeys import link_keys

def clean_body():
        #Select the body and make it active
        bpy.ops.object.mode_set(mode = 'OBJECT')
        body = bpy.data.objects['Body']
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        
        #Make UV map names clearer
        body.data.uv_layers[0].name = 'uv_main'
        body.data.uv_layers[1].name = 'uv_nipple_and_shine'
        body.data.uv_layers[2].name = 'uv_underhair'
        body.data.uv_layers[3].name = 'uv_eyeshadow'

        #rename the extra tongue material
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        def delete_material(mat_list):
            for mat in mat_list:
                mat_found = body.data.materials.find(mat)
                if mat_found > -1:
                    bpy.context.object.active_material_index = mat_found
                    bpy.ops.object.material_slot_select()
                else:
                    kklog('Material wasn\'t found when deleting body materials: ' + mat, 'warn')
            bpy.ops.mesh.delete(type='VERT')

        #check if there's a face material. If there isn't then the model most likely has a face02 face. Rename to correct name
        if body.data.materials.find('cf_m_face_00') == -1:
            for mat in body.data.materials:
                if 'cf_m_face_02 -' in mat.name:
                    mat.name = 'cf_m_face_00'

def add_freestyle_faces():
    body = bpy.data.objects['Body']
    #go into edit mode and deselect everything
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    #mark certain materials as freestyle faces
    def mark_as_freestyle(mat_list, search_type = 'exact'):
        for mat in mat_list:
            mat_found = body.data.materials.find(mat)      
            if mat_found > -1:
                bpy.context.object.active_material_index = mat_found
                bpy.ops.object.material_slot_select()
            else:
                kklog('Material wasn\'t found when freestyling body materials: ' + mat, 'warn')
        bpy.ops.mesh.mark_freestyle_face(clear=False)
    freestyle_list = [
        'cf_m_hitomi_00_cf_Ohitomi_R02',
        'cf_m_hitomi_00_cf_Ohitomi_L02',
        'cf_m_sirome_00.001',
        'cf_m_sirome_00',
        'cf_m_eyeline_kage',
        'cf_m_eyeline_down',
        'cf_m_eyeline_00_up',
        'cf_m_noseline_00',
        'cf_m_mayuge_00',]
    mark_as_freestyle(freestyle_list)
    bpy.ops.mesh.select_all(action = 'DESELECT')

    if bpy.context.scene.kkbp.sfw_mode:
        def mark_group_as_freestyle(group_list, search_type = 'exact'):
            for group in group_list:
                group_found = body.vertex_groups.find(group)      
                if group_found > -1:
                    bpy.context.object.active_material_index = group_found
                    bpy.ops.object.vertex_group_select()
                else:
                    kklog('Group wasn\'t found when freestyling vertex groups: ' + group, 'warn')
            bpy.ops.mesh.mark_freestyle_face(clear=False)
        freestyle_list = [
            'cf_j_bnip02_L', 'cf_j_bnip02_R'
            'cf_s_bust03_L', 'cf_s_bust03_R']
        mark_group_as_freestyle(freestyle_list)
        bpy.ops.mesh.select_all(action = 'DESELECT')

        def delete_group(group_list, search_type = 'exact'):
            bpy.ops.mesh.select_all(action = 'DESELECT')
            for group in group_list:
                group_found = body.vertex_groups.find(group)      
                if group_found > -1:
                    bpy.context.object.vertex_groups.active_index = group_found
                    bpy.ops.object.vertex_group_select()
                else:
                    kklog('Group wasn\'t found when deleting vertex groups: ' + group, 'warn')
            bpy.ops.mesh.delete(type='VERT')
        delete_list = [
            'cf_j_kokan', 'cf_j_ana'
            'cf_s_bnip025_L', 'cf_s_bnip025_R']
        delete_group(delete_list)
        bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

def separate_material(object, mat_list, search_type = 'exact'):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    #print(object)
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.mode_set(mode = 'EDIT')
    #print(object)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    for mat in mat_list:
        mat_found = -1
        #print(mat)
        if search_type == 'fuzzy' and ('cm_m_' in mat or 'c_m_' in mat or 'o_hit_' in mat or mat == 'cf_O_face_atari_M'):
            for matindex in range(0, len(object.data.materials), 1):
                if mat in object.data.materials[matindex].name:
                    mat_found = matindex
        else:
            mat_found = object.data.materials.find(mat)
        if mat_found > -1:
            bpy.context.object.active_material_index = mat_found
            #moves the materials in a specific order to prevent transparency issues on body
            def moveUp():
                return bpy.ops.object.material_slot_move(direction='UP')
            while moveUp() != {"CANCELLED"}:
                pass
            bpy.ops.object.material_slot_select()
        else:
            kklog('Material wasn\'t found when separating body materials: ' + mat, 'warn')
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.mode_set(mode = 'OBJECT')


def index_exists(list, index):
    if 0 <= index < len(list):
        return True
    else:
        return False

def separate_everything(context):
    body = bpy.data.objects['Body']

    #Select all materials that use the hair renderer and don't have a normal map then separate
    json_file = open(context.scene.kkbp.import_dir + 'KK_MaterialData.json')
    material_data = json.load(json_file)
    json_file = open(context.scene.kkbp.import_dir + 'KK_TextureData.json')
    texture_data = json.load(json_file)
    #get all texture files
    texture_files = []
    for file in texture_data:
        texture_files.append(file['textureName'])
    if context.scene.kkbp.categorize_dropdown not in ['B']:
        for outfit in bpy.data.objects:
            if "Outfit" in outfit.name and "Hair" not in outfit.name:
                #selection stuff
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action = 'DESELECT')
                bpy.context.view_layer.objects.active = outfit
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'DESELECT')

                outfit['KKBP outfit ID'] = int(outfit.name[-1:])

                #make uv names match body's names
                outfit.data.uv_layers[0].name = 'uv_main'
                outfit.data.uv_layers[1].name = 'uv_nipple_and_shine'
                outfit.data.uv_layers[2].name = 'uv_underhair'
                outfit.data.uv_layers[3].name = 'uv_eyeshadow'
                
                hair_mat_list = []
                for mat in material_data:
                    if mat['ShaderName'] in ["Shader Forge/main_hair_front", "Shader Forge/main_hair", 'Koikano/hair_main_sun_front', 'Koikano/hair_main_sun', 'xukmi/HairPlus', 'xukmi/HairFrontPlus']:
                        if (mat['MaterialName'] + '_HGLS.png') in texture_files or ((mat['MaterialName'] + '_NMP.png') not in texture_files and (mat['MaterialName'] + '_MT_CT.png') not in texture_files and (mat['MaterialName'] + '_MT.png') not in texture_files):
                            hair_mat_list.append(mat['MaterialName'])
                if len(hair_mat_list):
                    separate_material(outfit, hair_mat_list)
                    bpy.data.objects[outfit.name + '.001'].name = 'Hair ' + outfit.name

                    #don't reparent hair if Categorize by SMR
                    if context.scene.kkbp.categorize_dropdown not in ['D']:
                        bpy.data.objects['Hair ' + outfit.name].parent = outfit
        bpy.context.view_layer.objects.active = body
    
    if context.scene.kkbp.categorize_dropdown in ['A', 'B']:
        #Select any clothes pieces that are normally supposed to be hidden and hide them
        #the clothes json contains the clothing objects in a [base object, variation object, base object, variation object] format
        json_file = open(context.scene.kkbp.import_dir + 'KK_ClothesData.json')
        clothes_data = json.load(json_file)
        #the smr json contains the link between the clothing object and the clothing material. The material is used for separation
        json_file = open(context.scene.kkbp.import_dir + 'KK_SMRData.json')
        smr_data = json.load(json_file)

        clothes_labels = [
            'Top',
            'Bottom',
            'Bra',
            'Underwear',
            'Gloves',
            'Pantyhose',
            'Legwear',
            'Indoor shoes',
            'Outdoor shoes',
            'Top part A',
            'Top part B',
            'Top part C']
        
        def separate_pieces(piece, name_prefix = None):
            try:
                separate_material(piece, smr_index['SMRMaterialNames'])
                bpy.data.objects[piece.name + '.001'].parent = piece
                bpy.data.objects[piece.name + '.001'].name = name_prefix if name_prefix else (clothes_labels[clothes_index - 12 * outfit_index]) + ' alt ' + chr(ord('A') + label_index) + ' ' + piece.name
            except:
                #this piece was already separated
                pass
        
        def get_base_name(mat):
            return mat[:mat.rfind(' ')]
        
        #If there's multiple pieces to any clothing type, separate them into their own object using the smr data
        #skip indoor shoes and the Top, Top part A-C categories for now
        outfits = [outfit for outfit in bpy.data.objects if 'Outfit ' in outfit.name and 'Hair' not in outfit.name]
        for outfit in outfits:
            outfit_index = int(outfit.name[-3:]) if len(outfits) > 1 else 0 #change to 0 for single outfit exports
            clothes_indexes = [1, 2, 3, 4, 5, 6, 8] 
            clothes_indexes = [element + (12 * outfit_index) for element in clothes_indexes] #shift based on outfit number
            
            for clothes_index in clothes_indexes:
                variations = len(clothes_data[clothes_index]['RendNormal01'])
                if variations > 1:
                    label_index = 0
                    for index in range(1, variations):
                        previous_subpart_material_name = None
                        previous_subpart_object_name = clothes_data[clothes_index]['RendNormal01'][index-1]
                        for smr_index in smr_data:
                            if (smr_index['SMRName'] == previous_subpart_object_name and
                                smr_index['CoordinateType'] == int(outfit.name[-3:])):
                                previous_subpart_material_name = get_base_name(smr_index['SMRMaterialNames'][0])
                                break

                        current_subpart_object_name = clothes_data[clothes_index]['RendNormal01'][index]
                        for smr_index in smr_data:
                            if (smr_index['SMRName'] == current_subpart_object_name and
                                smr_index['CoordinateType'] == int(outfit.name[-3:]) and
                                previous_subpart_material_name == get_base_name(smr_index['SMRMaterialNames'][0])):
                                separate_pieces(outfit)
                                label_index+=1
                                break
        
        #separate indoor shoes
        #in a separate loop to prevent crashing
        outfits = [outfit for outfit in bpy.data.objects if 'Outfit ' in outfit.name and 'Hair' not in outfit.name and 'alt ' not in outfit.name and 'Indoor' not in outfit.name]
        for outfit in outfits:
            outfit_index = int(outfit.name[-3:]) if len(outfits) > 1 else 0 #change to 0 for single outfit exports
            clothes_index = 7 + (12 * outfit_index)
            
            #Always separate indoor shoes
            indoor_shoes_name = clothes_data[clothes_index]['RendNormal01']
            if indoor_shoes_name:
                for smr_index in smr_data:
                    if smr_index['SMRName'] == indoor_shoes_name[0] and smr_index['CoordinateType'] == outfit_index:
                        separate_material(outfit, smr_index['SMRMaterialNames'])
                        bpy.data.objects[outfit.name + '.001'].name = clothes_labels[7] + ' ' + outfit.name
                        bpy.data.objects[clothes_labels[7] + ' ' + outfit.name].parent = outfit

        #separate Top pieces and make sure to group them correctly
        #in a separate loop to prevent crashing
        outfits = [outfit for outfit in bpy.data.objects if 'Outfit ' in outfit.name and 'Hair' not in outfit.name and 'alt ' not in outfit.name and 'Indoor' not in outfit.name]
        for outfit in outfits:
            grouping = {}
            outfit_index = int(outfit.name[-3:]) if len(outfits) > 1 else 0 #change to 0 for single outfit exports
            clothes_indexes = [0, 9, 10, 11]
            clothes_indexes = [element + (12 * outfit_index) for element in clothes_indexes] #shift based on outfit number

            for clothes_index in clothes_indexes:
                #print(clothes_index)
                for cat in ['RendNormal01', 'RendEmblem01', 'RendEmblem02']:
                    variations = len(clothes_data[clothes_index][cat])
                    if variations > 1 or (variations == 1 and cat not in 'RendNormal01'):
                        clothes_to_separate = clothes_data[clothes_index][cat]
                        #kklog(clothes_to_separate)
                        if cat not in 'RendNormal01' and variations == 1:
                            clothes_to_separate = [clothes_to_separate]
                        if len(clothes_to_separate) > 1:
                            for index in range(1,len(clothes_to_separate)):
                                previous_subpart_material_name = None
                                previous_subpart_object_name = clothes_data[clothes_index][cat][index-1]
                                for smr_index in smr_data:
                                    if (smr_index['SMRName'] == previous_subpart_object_name and
                                        smr_index['CoordinateType'] == int(outfit.name[-3:])):
                                        previous_subpart_material_name = get_base_name(smr_index['SMRMaterialNames'][0])
                                        break

                                current_subpart_object_name = clothes_data[clothes_index][cat][index]
                                for smr_index in smr_data:
                                    if (smr_index['SMRName'] == current_subpart_object_name and
                                        smr_index['CoordinateType'] == int(outfit.name[-3:]) and
                                        previous_subpart_material_name == get_base_name(smr_index['SMRMaterialNames'][0])):
                                        for item in smr_index['SMRMaterialNames']:
                                            try:
                                                grouping[index].append(item)
                                            except:
                                                grouping[index] = [item]
                                        break
            if grouping != {}:
                label_index = 0
                for index in grouping:
                    separate_material(outfit, grouping[index])
                    bpy.data.objects[outfit.name + '.001'].parent = outfit
                    bpy.data.objects[outfit.name + '.001'].name = clothes_labels[0] + ' alt ' + chr(ord('A') + label_index) + ' ' + outfit.name
                    label_index+=1

    #Separate hitbox materials, if any
    hit_box_list = []
    for mat in material_data:
        if mat['MaterialName'][0:6] == 'o_hit_' or mat['MaterialName'] == 'cf_O_face_atari_M' or mat['MaterialName'] == 'cf_O_face_atari_M.001':
            hit_box_list.append(mat['MaterialName'])
    #kklog(hit_box_list)
    if len(hit_box_list):
        separate_material(body, hit_box_list)
        bpy.data.objects[body.name + '.001'].name = 'Hitboxes'
        if bpy.data.objects['Outfit 00'].material_slots.get('cf_O_face_atari_M.001'):
            #print('attempting to get the hitboxes off outfit 00')
            separate_material(bpy.data.objects['Outfit 00'], hit_box_list, search_type='fuzzy')
            bpy.data.objects['Outfit 00.001'].name = 'Hitboxes again'

    #Separate the shadowcast if any
    try:
        shad_mat_list = ['c_m_shadowcast', 'Standard']
        separate_material(body, shad_mat_list, 'fuzzy')
        bpy.data.objects[body.name + '.001'].name = 'Shadowcast'
    except:
        pass
    
    #Separate the bonelyfans mesh if any
    try:
        bone_mat_list = ['Bonelyfans', 'Bonelyfans.001']
        separate_material(body, bone_mat_list)
        bpy.data.objects[body.name + '.001'].name = 'Bonelyfans'
    except:
        pass

        #remove unused material slots on all objects
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.material_slot_remove_unused()
        
    def move_and_hide_collection (objects, new_collection):
        for object in objects:
            if bpy.data.objects.get(object):
                bpy.data.objects[object].select_set(True)
                bpy.context.view_layer.objects.active=bpy.data.objects[object]
        #move
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name=new_collection)
        #hide the new collection
        try:
            bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children[new_collection]
            bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
        except:
            try:
                #maybe the collection is in the default Collection collection
                bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection'].children[new_collection]
                bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
            except:
                #maybe the collection is already hidden, or doesn't exist
                pass

    #move these to their own collection
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    move_and_hide_collection(['Shadowcast', 'Bonelyfans'], "Shadowcast Collection")
    move_and_hide_collection(['Hitboxes', 'Hitboxes again'], "Hitbox Collection")

#merge certain materials for the body object to prevent odd shading issues later on
def fix_body_seams():
    bpy.ops.object.select_all(action='DESELECT')
    body = bpy.data.objects['Body']
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode = 'EDIT')
    seam_list = [
        'cm_m_body',
        'cf_m_body',
        'cf_m_face_00',
        'cf_m_face_00.001']
    for mat in seam_list:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
    bpy.ops.mesh.remove_doubles(threshold=0.00001)

def make_tear_and_gag_shapekeys():
    #Create a reverse shapekey for each tear and gag material
    body = bpy.data.objects['Body']
    armature = bpy.data.objects['Armature']
    bpy.context.view_layer.objects.active = body
    
    #Move tears and gag backwards on the basis shapekey
    tear_mats = {
        'cf_m_namida_00.002':   'Tears small',
        'cf_m_namida_00.001':   "Tears med",
        'cf_m_namida_00':       "Tears big",
        'cf_m_gageye_00':       "Gag eye 00",
        'cf_m_gageye_01':       "Gag eye 01",
        'cf_m_gageye_02':       "Gag eye 02"
    }
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    for mat in tear_mats:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
    #refresh selection, then move tears a random amount backwards
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.mode_set(mode = 'EDIT')
    selected_verts = [v for v in body.data.vertices if v.select]
    amount_to_move_tears_back = selected_verts[0].co.y - armature.data.bones['cf_j_head'].head.y
    bpy.ops.transform.translate(value=(0, abs(amount_to_move_tears_back), 0))

    #move the tears forwards again the same amount in individual shapekeys
    for mat in tear_mats:
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.shape_key_add(from_mix=False)
        last_shapekey = len(body.data.shape_keys.key_blocks)-1
        body.data.shape_keys.key_blocks[-1].name = tear_mats[mat]
        bpy.context.object.active_shape_key_index = last_shapekey
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
        #find a random vertex location of the tear and move it forwards
        bpy.ops.object.mode_set(mode = 'OBJECT')
        selected_verts = [v for v in body.data.vertices if v.select]
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.transform.translate(value=(0, -1 * abs(amount_to_move_tears_back), 0))
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.shape_key_move(type='TOP' if 'cf_m_namida_00' in mat else 'BOTTOM')

    #Merge the tear materials
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    tear_mats = ['cf_m_namida_00.001', 'cf_m_namida_00.002']
    for mat in tear_mats:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
        bpy.context.object.active_material_index = body.data.materials.find('cf_m_namida_00')
        bpy.ops.object.material_slot_assign()
        bpy.ops.mesh.select_all(action='DESELECT')

    #make a vertex group that does not contain the tears
    bpy.ops.object.vertex_group_add()
    bpy.ops.mesh.select_all(action='SELECT')
    body.vertex_groups.active.name = "Body without Tears"
    bpy.context.object.active_material_index = body.data.materials.find('cf_m_namida_00')
    bpy.ops.object.material_slot_deselect()
    bpy.ops.object.vertex_group_assign()

    #Separate tears from body object, parent it to the body so it's hidden in the outliner
    #link shapekeys of tears to body
    tearMats = ['cf_m_namida_00']
    separate_material(body, tearMats)
    tears = bpy.data.objects['Body.001']
    tears.name = 'Tears'
    tears.parent = bpy.data.objects['Body']
    bpy.ops.object.mode_set(mode = 'OBJECT')
    link_keys(body, [tears])

    #create real gag eye shapekeys
    bpy.context.view_layer.objects.active=body
    gag_keys = [
        'Circle Eyes 1',
        'Circle Eyes 2',
        'Spiral Eyes',
        'Heart Eyes',
        'Fiery Eyes',
        'Cartoony Wink',
        'Vertical Line',
        'Cartoony Closed',
        'Horizontal Line',
        'Cartoony Crying' 
    ]
    for key in gag_keys:
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.shape_key_add(from_mix=False)
        last_shapekey = len(body.data.shape_keys.key_blocks)-1
        body.data.shape_keys.key_blocks[-1].name = key
        bpy.context.object.active_shape_key_index = last_shapekey
        bpy.ops.object.shape_key_move(type='TOP')

    #make most gag eye shapekeys activate the body's gag key
    skey_driver = bpy.data.shape_keys[0].key_blocks['KK Eyes_gageye'].driver_add('value')
    skey_driver.driver.type = 'SCRIPTED'
    for key in gag_keys:
        newVar = skey_driver.driver.variables.new()
        newVar.name = key.replace(' ','')
        newVar.type = 'SINGLE_PROP'
        newVar.targets[0].id_type = 'KEY'
        newVar.targets[0].id = body.data.shape_keys
        newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
    condition = [key.replace(' ', '') for key in gag_keys if 'Fiery' not in key]
    skey_driver.driver.expression = '1 if ' + ' or '.join(condition) + ' else 0'

    #make certain gag eye shapekeys activate the correct gag show key
    skey_driver = bpy.data.shape_keys[0].key_blocks['Gag eye 00'].driver_add('value')
    skey_driver.driver.type = 'SCRIPTED'
    for key in gag_keys:
        newVar = skey_driver.driver.variables.new()
        newVar.name = key.replace(' ','')
        newVar.type = 'SINGLE_PROP'
        newVar.targets[0].id_type = 'KEY'
        newVar.targets[0].id = body.data.shape_keys
        newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
    skey_driver.driver.expression = '1 if CircleEyes1 or CircleEyes2 or VerticalLine or CartoonyClosed or HorizontalLine else 0'

    #make certain gag eye shapekeys activate the correct gag show key
    skey_driver = bpy.data.shape_keys[0].key_blocks['Gag eye 01'].driver_add('value')
    skey_driver.driver.type = 'SCRIPTED'
    for key in gag_keys:
        newVar = skey_driver.driver.variables.new()
        newVar.name = key.replace(' ','')
        newVar.type = 'SINGLE_PROP'
        newVar.targets[0].id_type = 'KEY'
        newVar.targets[0].id = body.data.shape_keys
        newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
    skey_driver.driver.expression = '1 if HeartEyes or SpiralEyes else 0'

    #make certain gag eye shapekeys activate the correct gag show key
    skey_driver = bpy.data.shape_keys[0].key_blocks['Gag eye 02'].driver_add('value')
    skey_driver.driver.type = 'SCRIPTED'
    for key in gag_keys:
        newVar = skey_driver.driver.variables.new()
        newVar.name = key.replace(' ','')
        newVar.type = 'SINGLE_PROP'
        newVar.targets[0].id_type = 'KEY'
        newVar.targets[0].id = body.data.shape_keys
        newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
    skey_driver.driver.expression = '1 if FieryEyes or CartoonyWink or CartoonyCrying else 0'

    #make a vertex group that does not contain the gag_eyes
    bpy.ops.object.vertex_group_add()
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    body.vertex_groups.active.name = "Body without Gag eyes"
    for gag_mat in ['cf_m_gageye_00', 'cf_m_gageye_01', 'cf_m_gageye_02']:
        bpy.context.object.active_material_index = body.data.materials.find(gag_mat)
        bpy.ops.object.material_slot_deselect()
    bpy.ops.object.vertex_group_assign()

    #Separate gag from body object, parent it to the body so it's hidden in the outliner
    #link shapekeys of gag to body
    gag_mat = ['cf_m_gageye_00', 'cf_m_gageye_01', 'cf_m_gageye_02']
    separate_material(body, gag_mat)
    gag = bpy.data.objects['Body.001']
    gag.name = 'Gag Eyes'
    gag.parent = bpy.data.objects['Body']
    bpy.ops.object.mode_set(mode = 'OBJECT')
    link_keys(body, [gag])

    if bpy.context.scene.kkbp.categorize_dropdown != 'D' and bpy.data.materials.get('cf_m_tang.001'):
        #Separate rigged tongue from body object, parent it to the body so it's hidden in the outliner
        #link shapekeys of tongue to body even though it doesn't have them
        tongueMats = ['cf_m_tang.001']
        separate_material(body, tongueMats)
        tongue = bpy.data.objects['Body.001']
        tongue.name = 'Tongue (rigged)'
        tongue.parent = bpy.data.objects['Body']
        bpy.ops.object.mode_set(mode = 'OBJECT')
        link_keys(body, [tongue])
        tongue.hide = True

def remove_duplicate_slots():
    for obj in bpy.data.objects:
        if 'Body' == obj.name or 'Indoor shoes Outfit ' in obj.name or 'Outfit ' in obj.name or 'Hair' in obj.name:
            #combine duplicated material slots
            bpy.ops.object.material_slot_remove_unused()
            mesh = obj
            bpy.ops.object.select_all(action='DESELECT')
            mesh.select_set(True)
            bpy.context.view_layer.objects.active=mesh
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            
            #remap duplicate materials to the base one
            material_list = mesh.data.materials
            for mat in material_list:
                mat_name_list = [
                    'cf_m_hitomi_00_cf_Ohitomi_L02',
                    'cf_m_hitomi_00_cf_Ohitomi_R02',
                    'cf_m_sirome_00',
                    'cf_m_sirome_00.001',
                    'cf_m_namida_00',
                    'cf_m_namida_00.001',
                    'cf_m_namida_00.002',
                    'cf_m_tang',
                    'cf_m_tang.001',
                ]
                #don't merge the above materials if categorize by SMR is chosen.
                eye_flag = mat.name not in mat_name_list and bpy.context.scene.kkbp.categorize_dropdown != 'D'
                
                if '.' in mat.name[-4:] and eye_flag:
                    try:
                        #the material name is normal
                        base_name, dupe_number = mat.name.split('.',2)
                    except:
                        #someone (not naming names) left a .### in the material name
                        base_name, rest_of_base_name, dupe_number = mat.name.split('.',2)
                        base_name = base_name + rest_of_base_name
                    #remap material if it's a dupe, but don't touch the eye dupe
                    if material_list.get(base_name) and int(dupe_number) and 'cf_m_hitomi_00' not in base_name:
                        mat.user_remap(material_list[base_name])
                        bpy.data.materials.remove(mat)
                    else:
                        kklog("Somehow found a false duplicate material but didn't merge: " + mat.name, 'warn')
            
            #then clean material slots by going through each slot and reassigning the slots that are repeated
            repeats = {}
            for index, mat in enumerate(material_list):
                if mat.name not in repeats:
                    repeats[mat.name] = [index]
                    # print("First entry of {} in slot {}".format(mat.name, index))
                else:
                    repeats[mat.name].append(index)
                    # print("Additional entry of {} in slot {}".format(mat.name, index))
            
            for material_name in list(repeats.keys()):
                if len(repeats[material_name]) > 1:
                    for repeated_slot in repeats[material_name]:
                        #don't touch the first slot
                        if repeated_slot == repeats[material_name][0]:
                            continue
                        kklog("Moving duplicate material {} in slot {} to the original slot {}".format(material_name, repeated_slot, repeats[material_name][0]))
                        mesh.active_material_index = repeated_slot
                        bpy.ops.object.material_slot_select()
                        mesh.active_material_index = repeats[material_name][0]
                        bpy.ops.object.material_slot_assign()
                        bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.material_slot_remove_unused()

def cleanup():
    #remove shapekeys on all objects except the body/tears because only those need them
    for obj in bpy.data.objects:
        if obj.name not in ['Body','Tears','Gag Eyes'] and obj.type == 'MESH':
            if not obj.data.shape_keys:
                continue
            
            for key in obj.data.shape_keys.key_blocks.keys():
                obj.shape_key_remove(obj.data.shape_keys.key_blocks[key])

    #try to make sure we are in object mode
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    
    #then make sure body is the active context
    bpy.context.view_layer.objects.active = bpy.data.objects['Body']
    
    #remove unused material slots for all visible objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.material_slot_remove_unused()
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
        #if ' alt ' in obj.name or 'Indoor shoes' in obj.name:
            #obj.hide = True
            #obj.hide_render = True
    bpy.ops.object.select_all(action='DESELECT')

    #and clean up the oprhaned data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)

    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

class separate_body(bpy.types.Operator):
    bl_idname = "kkb.separatebody"
    bl_label = "The separate body script"
    bl_description = "Separates the Body, shadowcast and bonelyfans into separate objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            last_step = time.time()
            kklog('\nSeparating body, clothes, hair, hitboxes and shadowcast, then removing duplicate materials...')
            
            clean_body()
            add_freestyle_faces()
            remove_duplicate_slots()
            separate_everything(context)
            if context.scene.kkbp.fix_seams:
                fix_body_seams()
            
            #make tear and gageye shapekeys if shapekey modifications are enabled
            if context.scene.kkbp.shapekeys_dropdown != 'C':
                make_tear_and_gag_shapekeys()
                
            cleanup()

            kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
                    #if it fails then abort and print the error
            return{'FINISHED'}

        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(separate_body)

    # test call
    print((bpy.ops.kkb.separatebody('INVOKE_DEFAULT')))
