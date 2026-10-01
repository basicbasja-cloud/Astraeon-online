"""Validate data against the four public schemas (requires jsonschema)."""
import json
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def validate(name,data):
 schema=json.loads((ROOT/'world/v3/schemas'/name).read_text());jsonschema.Draft202012Validator.check_schema(schema);jsonschema.validate(data,schema)
for name in ['golden-proof','wayfarer-court']:
 scene=json.loads((ROOT/'world/v3'/(name+'.json')).read_text())
 validate('terrain.schema.json',scene['terrain']);validate('navigation.schema.json',scene['navigation'])
 for o in scene['objects']:validate('town-object.schema.json',o)
validate('animation-manifest.schema.json',json.loads((ROOT/'world/v3/warrior-animation.json').read_text()))
print('PASS Terrain, Navigation, TownObject and AnimationManifest schemas')
