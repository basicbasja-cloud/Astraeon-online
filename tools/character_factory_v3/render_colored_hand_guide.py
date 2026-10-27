"""Blender-only hand-orientation guide capture. Never final character art."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from bpy.app.handlers import persistent
from render_frozen_patch001_guides import run_capture


def main(renderer_main=None):
    argv=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(argv[argv.index('--job')+1]).read_text());output=Path(argv[argv.index('--output')+1])
    if job.get('hand_color_guide_revision')!=1:raise ValueError('Explicit isolated hand-color guide job required')
    if output.exists():raise ValueError('Use a fresh hand-guide output')
    painted=[]
    @persistent
    def colors(scene):
        scene.display.shading.color_type='VERTEX'
        for obj in [o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render]:
            mesh=obj.data
            if mesh.color_attributes.get('GuideHandColors'):continue
            layer=mesh.color_attributes.new(name='GuideHandColors',type='FLOAT_COLOR',domain='POINT')
            data=[]
            for vertex in mesh.vertices:
                groups={obj.vertex_groups[g.group].name:g.weight for g in vertex.groups}
                hand=lambda side:sum(w for name,w in groups.items() if name.endswith('_'+side) and (name.startswith(('hand_','index_','middle_','ring_','pinky_','thumb_'))))
                right=min(1,hand('r'));left=min(1,hand('l'));thumb=sum(w for name,w in groups.items() if name.startswith('thumb_') and name.endswith('_r'));index=sum(w for name,w in groups.items() if name.startswith('index_') and name.endswith('_r'))
                color=[.55,.6,.62]
                if groups:
                    target=[.24,.10,.045] if right>=left else [.35,.16,.48];weight=max(right,left)
                    color=[a*(1-weight)+b*weight for a,b in zip(color,target)]
                    if thumb>.25:color=[a*(1-thumb)+b*thumb for a,b in zip(color,[.9,.5,.07])]
                    if index>.25:color=[a*(1-index)+b*index for a,b in zip(color,[.05,.6,.72])]
                elif mesh.materials:color=list(mesh.materials[0].diffuse_color[:3])
                data.extend([*color,1])
            layer.data.foreach_set('color',data);mesh.color_attributes.active_color_name=layer.name;painted.append({'mesh':obj.name,'vertices':len(mesh.vertices)})
    bpy.app.handlers.render_pre.append(colors)
    try:run_capture(renderer_main=renderer_main)
    finally:
        if colors in bpy.app.handlers.render_pre:bpy.app.handlers.render_pre.remove(colors)
    (output/'hand-color-guide-receipt.json').write_text(json.dumps({'status':'SOURCE_HAND_ORIENTATION_GUIDE_NOT_SPRITE_ART','meshes':painted,'color_semantics':{'right_hand':'brown','left_hand':'violet','right_thumb':'ochre','right_index':'cyan'},'geometry_and_motion_modified':False,'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'runtime_admitted':False},indent=2)+'\n')

if __name__=='__main__':main()
