"""Import authorized cached FBX/glTF references into separate owned scenes.

Archive hashes and license evidence must match FREE_ASSET_PROVENANCE.json.
This imports data formats through Blender operators, never external .blend code.
Do not run on an occupied inspection scene; the live imports are already done.
"""
import bpy

cache='C:/Users/Lenovo/Bas/Astra online/.character-tools/free-assets/'
jobs=[
 ('ASTRAEON_FREE_BASE_INSPECTION','GLTF',cache+'quaternius-base-standard/extracted/Universal Base Characters[Standard]/Base Characters/Godot - UE/Superhero_Male_FullBody.gltf'),
 ('ASTRAEON_FREE_FBX_INSPECTION','FBX',cache+'quaternius-base-standard/extracted/Universal Base Characters[Standard]/Base Characters/Unity/Superhero_Male_FullBody.fbx'),
 ('ASTRAEON_FREE_OUTFIT_INSPECTION','FBX',cache+'quaternius-fantasy-standard/extracted/Modular Character Outfits - Fantasy[Standard]/Exports/FBX (Unity)/Outfits/Male_Ranger.fbx'),
]
# Check the whole batch before mutating any scene.
for name,kind,path in jobs:
    old=bpy.data.scenes.get(name)
    assert old is None or len(old.objects)==0,'Inspection scene already contains an import: '+name
for name,kind,path in jobs:
    scene=bpy.data.scenes.get(name) or bpy.data.scenes.new(name);bpy.context.window.scene=scene
    if kind=='GLTF':bpy.ops.import_scene.gltf(filepath=path)
    else:bpy.ops.import_scene.fbx(filepath=path)
    scene['purpose']='Authorized free-asset inspection; not character approval'
    scene['creator']='Quaternius';scene['archiveLicense']='CC0-1.0';scene['currentSiteTerms']='QAL v1.0; see FREE_ASSET_PROVENANCE.json'
    scene['ownerApproved']=False;scene['runtimeAdmitted']=False
    print('REFERENCE_IMPORTED',name,len(scene.objects))
