"""Recreate workspace-local SPA; optionally compile the pinned Aseprite source for local use."""
from pathlib import Path
import argparse,json,subprocess,os,sys
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work/tool-runtime'
PINS={'spa':'ee2ea8f027bafdbed4f040c8288a1095b287e8b8','aseprite':'b3e34acbae812b8a1d814c2e6285343b351c8945'}
def run(args,**kw):subprocess.run([str(x)for x in args],check=True,cwd=ROOT,**kw)
def checkout(name,url):
 p=WORK/(name+'-source')
 if not(p/'.git').exists():run(['git','clone','--depth','1',url,p])
 current=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()
 if current!=PINS[name]:
  run(['git','-C',p,'fetch','--depth','1','origin',PINS[name]]);run(['git','-C',p,'checkout','--detach',PINS[name]])
 return p
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build-aseprite',action='store_true');a=p.parse_args();WORK.mkdir(parents=True,exist_ok=True);env=WORK/'spa-env';python=env/'bin/python'
 if not python.exists():run(['uv','venv','--python','3.13',env])
 run(['uv','pip','install','--python',python,'aseprite-automation==0.5.0']);run([env/'bin/spa','version']);run(['uv','pip','install','--python',python,'-r',ROOT/'.agents/skills/img2game2d/forge/requirements.txt'])
 if a.build_aseprite:
  run(['uv','pip','install','--python',python,'cmake==4.4.4','ninja==1.13.2'])
  source=checkout('aseprite','https://github.com/aseprite/aseprite.git');run(['git','-C',source,'submodule','update','--init','--recursive','--depth','1'])
  run([sys.executable,ROOT/'tools/sprite-x11-build-deps.py']);prefix=WORK/'x11/sysroot/usr';build=WORK/'aseprite-build';settings=os.environ.copy();settings['PATH']=str(env/'bin')+os.pathsep+settings['PATH']
  flags=['-DCMAKE_BUILD_TYPE=Release','-DLAF_BACKEND=none','-DLAF_WITH_CLIP=ON','-DCLIP_X11_WITH_PNG=OFF','-DLAF_WITH_EXAMPLES=OFF','-DLAF_WITH_TESTS=OFF','-DENABLE_NEWS=OFF','-DENABLE_UPDATER=OFF','-DENABLE_WEBSOCKET=OFF','-DENABLE_WEBP=OFF','-DENABLE_TESTS=OFF','-DCMAKE_POLICY_VERSION_MINIMUM=3.5',f'-DCMAKE_PREFIX_PATH={prefix}',f'-DCMAKE_CXX_FLAGS=-I{prefix}/include',f'-DCMAKE_C_FLAGS=-I{prefix}/include',f'-DCMAKE_EXE_LINKER_FLAGS=-L{prefix}/lib/x86_64-linux-gnu']
  run([env/'bin/cmake','-S',source,'-B',build,'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(env/'bin/ninja'),'-U','HAVE_XCB_XLIB_H',*flags],env=settings)
  run([env/'bin/cmake','--build',build,'--target','aseprite','--parallel','4'],env=settings)
  run([env/'bin/spa','info','--aseprite',build/'bin/aseprite'])
 print('SPA:',env/'bin/spa');print('Aseprite source builds stay local; binaries are not redistributed in the research repository.')
if __name__=='__main__':main()
