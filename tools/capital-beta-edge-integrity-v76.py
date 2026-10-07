"""Hash every source field except the explicitly allowed beta-edge changes."""
import json,hashlib
def preserved_digest(source):
    data={**source,'objects':[o for o in source['objects'] if o['id']!='capital-beta-frontage-groundcover']}
    terrain={**source['terrain']}
    if terrain['material']=='publicTownStone':terrain.pop('uvs',None)
    terrain['surfaces']=[{k:v for k,v in a.items() if not (k=='uvs' and a['material']=='publicTownStone')} for a in terrain['surfaces']]
    data['terrain']=terrain;data['materials']={**source['materials']}
    material={**data['materials']['publicTownStone']};material['texture']={k:v for k,v in material['texture'].items() if k!='worldSize'}
    data['materials']['publicTownStone']=material
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
