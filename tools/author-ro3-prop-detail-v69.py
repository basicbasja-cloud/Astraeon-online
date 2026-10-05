"""Bring previously plain visible city props onto shared native detail textures."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert not scene.get('ro3_prop_detail_version');art=json.loads((ROOT/'authoring/materials/wayfarer-prop-detail-v69.json').read_text());updated={}
for kind,names in {'metal':['iron','gold','civicGold','teal'],'cloth':['clothOchre','clothRose','sailIvory','shopAwningSage'],'petal':['flowers','flowerRose','flowerIvory'],'rind':['produceGreen','produceRose','produceOchre'],'paper':['questParchment']}.items():
 for name in names:
  m=bpy.data.materials[name];assert not m.get('texture_json'),name;m['texture_json']=json.dumps(art['materials']['wayfarer-prop-'+kind+'-v69']['texture']);updated[name]=kind
for name,source in [('statueIvory','cream'),('shrineAzure','glass'),('waterLight','water')]:
 m=bpy.data.materials[name];assert not m.get('texture_json'),name;spec=json.loads(bpy.data.materials[source]['texture_json']);spec['anisotropy']=4;spec['paletteDetail']=.42;m['texture_json']=json.dumps(spec);updated[name]='shared '+source
exceptions={'forgeEmber','forgeHotCore','lanternGlow','lanternLight','marketAmber'}
used={o.data.materials[0].name for o in bpy.data.objects if o.type=='MESH' and o.get('render_visible',True) and o.data.materials};plain=sorted(name for name in used if not bpy.data.materials[name].get('texture_json'))
assert set(plain)<=exceptions,plain
scene['ro3_prop_detail_version']=69;scene['ro3_prop_detail_review_json']=json.dumps({'updatedMaterials':updated,'originalArtwork':art,'remainingVisiblePlainMaterials':plain,'plainMaterialPurpose':'Intentional light/fire color only; ordinary visible city surfaces have native textures','geometryAndPalettePreserved':True})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS material coverage:',len(updated),'previously plain materials; remaining plain are intentional glow/fire:',plain)
