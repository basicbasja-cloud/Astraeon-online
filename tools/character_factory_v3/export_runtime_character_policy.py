"""Export the six-character presentation policy; never mark artwork ready."""
import json
from pathlib import Path
from patch001_factory import ROOT,BASE,read

def policy(config):
    classes={}
    for name,klass in config['classes'].items():
        classes[str(klass['game_class_index'])]={'id':name.lower(),'name':name,'archetype':klass['game_archetype'],'clips':list(klass['actions']),'combatBindings':klass['combat_bindings'],'actions':{name:{'frames':action['frames'],'directions':action['authored_directions'],'directionMap':action['direction_map'],'loop':action['loop']}for name,action in klass['actions'].items()}}
    canvas=config['canvas'];characters={}
    for character in config['characters']:
        characters[character['class'].lower()+'/'+character['body_variant']]={'id':character['id'],'definition':'./assets/characters/'+character['id']+'/sprite.json','fitId':character['anatomy_fit_id']}
    return {'patch':config['patch'],'anatomy':{'frameWidth':canvas['runtime'][0],'frameHeight':canvas['runtime'][1],'rootAnchorX':canvas['runtime_root'][0],'rootAnchorY':canvas['runtime_root'][1],'referenceHeight':canvas['runtime_reference_height']},'classes':classes,'characters':characters,'mirroring':'none','artReady':False}

def render(config):
    return '''/* Generated from factory-v3/patch-0.0.1/factory.json; policy is not art approval. */
(function(scope){'use strict';
const freeze=o=>{if(o&&typeof o==='object'){Object.values(o).forEach(freeze);Object.freeze(o)}return o};
const policy=freeze('''+json.dumps(policy(config),indent=2)+''');
function classFor(index){return policy.classes[index]||null}
function characterFor(index,body){const c=classFor(index);return c?policy.characters[c.id+'/'+body]||null:null}
function clipsFor(index){return classFor(index)?.clips||[]}
function actionClip(index,id){return classFor(index)?.combatBindings[id]||null}
function validatePackage(d,index,body){
 const errors=[],c=classFor(index),character=characterFor(index,body);
 if(!character)return ['Unsupported patch class/body'];
 if(d.characterId!==character.id||d.classId!==c.name||d.bodyVariant!==body)errors.push('Character identity differs from selected class/body');
 for(const [key,value]of Object.entries(policy.anatomy))if(d.canvas?.[key]!==value)errors.push('Patch anatomy differs: '+key);
 if(d.mirroring!=='none'||d.layerMode!=='visible-cutout')errors.push('Patch needs real views and visible cutouts');
 for(const [name,expected]of Object.entries(c.actions)){
  const clip=d.clips?.[name];if(!clip){errors.push('Missing animation '+name);continue}
  if(clip.tags?.includes('PENDING_PRODUCTION'))errors.push('Pending animation '+name);
  if(clip.durations?.length!==expected.frames||clip.loop!==expected.loop)errors.push('Animation timeline differs: '+name);
  const authored=clip.authoredDirections||Object.keys(clip.directions||{});
  if(JSON.stringify(authored)!==JSON.stringify(expected.directions))errors.push('Authored direction policy differs: '+name);
  if(expected.directions.length===4&&JSON.stringify(clip.directionMap)!==JSON.stringify(expected.directionMap))errors.push('Facing map differs: '+name);
 }
 return errors;
}
const api=Object.freeze({policy,classFor,characterFor,clipsFor,actionClip,validatePackage});scope.AstraeonPatch001Characters=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
'''

if __name__=='__main__':
    (ROOT/'patch001-characters.js').write_text(render(read(BASE/'factory.json')))
