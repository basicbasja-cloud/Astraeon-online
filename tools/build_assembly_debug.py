#!/usr/bin/env python3
"""Bake obviously non-production raster shapes for assembly tests; no painted art."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DIRECTIONS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]


def build(output_root: Path) -> None:
    motion_dir = output_root/"authoring/characters/motion-templates/assembly-debug"
    subprocess.run(["node", str(ROOT/"tools/build-character-assembly-proof.cjs"), str(motion_dir)], check=True)
    template = json.loads((motion_dir/"motion-template.json").read_text())
    assets = output_root/"assets/characters/assembly-debug-v1"
    assets.mkdir(parents=True, exist_ok=True)
    atlases, hashes, parts = {}, {}, {}

    def atlas(name: str, rows: list[list[Image.Image]], tile=(32, 32)) -> list[list[dict]]:
        cols = max(len(row) for row in rows)
        image = Image.new("RGBA", (tile[0]*cols, tile[1]*len(rows)))
        refs = []
        for y, row in enumerate(rows):
            rr = []
            for x, cell in enumerate(row):
                if cell.size != tile or cell.mode != "RGBA":
                    raise ValueError("Shared raster convention mismatch")
                image.alpha_composite(cell, (x*tile[0], y*tile[1]))
                rr.append({"atlasId": name, "rect": [x*tile[0], y*tile[1], *tile]})
            refs.append(rr)
        file = assets/(name+".png")
        image.save(file)
        atlases[name] = {"file": file.relative_to(output_root).as_posix(), "width": image.width, "height": image.height}
        hashes[name] = hashlib.sha256(file.read_bytes()).hexdigest()
        return refs

    def cell(kind: str, direction: int, phase=0) -> Image.Image:
        im = Image.new("RGBA", (32, 32));d = ImageDraw.Draw(im)
        if kind == "head":
            d.ellipse((6, 5, 26, 26), fill="#f8c495")
            a=math.pi/2+direction*math.pi/4
            x,y=16+6*math.cos(a),16+6*math.sin(a)
            d.rectangle((x-2,y-2,x+2,y+2),fill="#704e37")
        elif kind.startswith("hair"):
            color = "#a358ea" if kind == "hair-a" else "#6636c9"
            for x in ([7,13,20] if kind=="hair-a" else [4,9,14,19,24]):
                d.polygon([(x,14),(x+3,3+phase),(x+7,14)],fill=color)
            d.rectangle((7,11,25,17+phase),fill=color)
        elif kind.startswith("weapon"):
            if kind=="weapon-a":d.rectangle((14,2,18,26),fill="#ef414b")
            else:d.polygon([(16,1),(6,14),(16,22),(26,14)],fill="#ff7879")
            d.rectangle((9,23,23,26),fill="#a52535");d.rectangle((14,26,18,31),fill="#ef414b")
        elif kind=="offhand":
            d.ellipse((4,4,28,29),fill="#f5d53f",outline="#9c7812",width=2)
            d.line((16,8,16,26),fill="#fff1a3",width=3)
        elif kind.startswith("headgear"):
            if kind=="headgear-a":d.rectangle((5,8,27,17),fill="#45e5ef")
            else:d.polygon([(4,18),(8,4),(16,14),(24,4),(28,18)],fill="#75f8fc")
        elif kind=="fx":
            d.ellipse((5+phase*6,7,11+phase*6,13),fill="#f576da")
        return im

    for body_id,color in [("body-blue","#3e8ceb"),("body-coral","#ee8766")]:
        timelines = {}
        for action,a in template["actions"].items():
            rows = []
            for di,direction in enumerate(DIRECTIONS):
                row=[]
                for f in a["directions"][direction]["frames"]:
                    im=Image.new("RGBA",(128,128));d=ImageDraw.Draw(im)
                    head=f["anchors"]["head"];waist=f["anchors"]["waist"]
                    d.rounded_rectangle((48,head["y"]+14,80,waist["y"]+11),radius=3,fill=color)
                    d.rectangle((53,waist["y"]+8,61,112),fill=color)
                    d.rectangle((67,waist["y"]+8,75,112),fill=color)
                    for anchor in ["mainHand","offHand"]:
                        p=f["anchors"][anchor];d.ellipse((p["x"]-4,p["y"]-4,p["x"]+4,p["y"]+4),fill=color)
                    aview=math.pi/2+di*math.pi/4
                    px,py=64+10*math.cos(aview),72+10*math.sin(aview)
                    d.line((64,72,px,py),fill="white",width=3)
                    d.ellipse((px-2,py-2,px+2,py+2),fill="white")
                    row.append(im)
                rows.append(row)
            refs=atlas(body_id+"-"+action.lower(),rows,(128,128))
            timelines[action]={direction:{"frames":[{"layers":{"Body":ref}} for ref in refs[i]]} for i,direction in enumerate(DIRECTIONS)}
        parts[body_id]={"slot":"Body","mode":"BODY_SYNC","space":"canvas","timelines":timelines}

    for part_id,layer,slot,anchor,pivot in [
        ("head","HeadBase","Head","head",[16,16]),
        ("weapon-a","MainHand","MainHand","mainHand",[16,28]),
        ("weapon-b","MainHand","MainHand","mainHand",[16,28]),
        ("offhand","OffHand","OffHand","offHand",[16,16]),
        ("headgear-a","HeadgearTop","Headgear","head",[16,26]),
        ("headgear-b","HeadgearTop","Headgear","head",[16,26])]:
        refs=atlas(part_id,[[cell(part_id,di)] for di in range(8)])
        parts[part_id]={"slot":slot,"mode":"ANCHOR_HOLD","space":"attachment","anchor":anchor,"timelines":{"*":{direction:{"views":[{"at":0,"layers":{layer:{**refs[i][0],"pivot":pivot}}}]} for i,direction in enumerate(DIRECTIONS)}}}

    for hair in ["hair-a","hair-b"]:
        backs=atlas(hair+"-back",[[cell(hair,di,k) for k in range(3)] for di in range(8)])
        fronts=atlas(hair+"-front",[[cell(hair,di,k) for k in range(3)] for di in range(8)])
        parts[hair]={"slot":"Hair","mode":"PHASE_SYNC","space":"attachment","anchor":"head","timelines":{"*":{direction:{"phases":[{"at":at,"layers":{"HairBack":{**backs[i][k],"pivot":[16,15],"localTransform":{"x":0,"y":1,"rotation":0,"scale":1}},"HairFront":{**fronts[i][k],"pivot":[16,24]}}} for k,at in enumerate([0,.4,.75])]} for i,direction in enumerate(DIRECTIONS)}}}

    garment_timelines={}
    for action,a in template["actions"].items():
        rows,frontrows=[],[]
        for direction in DIRECTIONS:
            row,fr=[],[]
            for f in a["directions"][direction]["frames"]:
                x,y=f["anchors"]["back"]["x"],f["anchors"]["back"]["y"]
                im=Image.new("RGBA",(128,128));d=ImageDraw.Draw(im)
                d.polygon([(x-14,y),(x+14,y),(x+26,y+41),(x-23,y+41)],fill="#45b46b")
                front=Image.new("RGBA",(128,128));df=ImageDraw.Draw(front)
                df.rectangle((x-16,y+4,x-11,y+18),fill="#68d185")
                row.append(im);fr.append(front)
            rows.append(row);frontrows.append(fr)
        backrefs=atlas("garment-back-"+action.lower(),rows,(128,128))
        frontrefs=atlas("garment-front-"+action.lower(),frontrows,(128,128))
        garment_timelines[action]={direction:{"frames":[{"layers":{"GarmentBack":backrefs[i][k],"GarmentFront":frontrefs[i][k]}} for k in range(len(backrefs[i]))]} for i,direction in enumerate(DIRECTIONS)}
    parts["garment"]={"slot":"Garment","mode":"BODY_SYNC","space":"canvas","timelines":garment_timelines}
    fxrefs=atlas("cosmetic-fx",[[cell("fx",i,k) for k in range(3)] for i in range(8)])
    parts["fx"]={"slot":"CosmeticFX","mode":"OWN_LOOP","space":"attachment","anchor":"fxOrigin","timelines":{"*":{direction:{"frames":[{"durationMs":duration,"layers":{"CosmeticFX":{**fxrefs[i][k],"pivot":[16,16]}}} for k,duration in enumerate([80,120,160])]} for i,direction in enumerate(DIRECTIONS)}}}
    slots={"Body":{"layers":["Body"],"required":True},"Head":{"layers":["HeadBase"],"required":True},"Hair":{"layers":["HairBack","HairFront"],"required":False},"MainHand":{"layers":["MainHand"],"required":False},"OffHand":{"layers":["OffHand"],"required":False},"Headgear":{"layers":["HeadgearTop"],"required":False},"Garment":{"layers":["GarmentBack","GarmentFront"],"required":False},"CosmeticFX":{"layers":["CosmeticFX"],"required":False}}
    defaults={"Body":"body-blue","Head":"head","Hair":"hair-a","MainHand":"weapon-a","OffHand":"offhand","Headgear":"headgear-a","Garment":"garment","CosmeticFX":"fx"}
    base={"schemaVersion":"1.0","packId":"debug-blue-v1","status":"DEV_ONLY","source":{"reference":"tools/build_assembly_debug.py","purpose":"Non-production shape calibration; no RO pixels or ASTRAEON costume art"},"compatibleMotionTemplates":[template["motionTemplateId"]],"registration":template["registration"],"mirroring":"none","slots":slots,"defaultParts":defaults,"parts":parts,"atlases":atlases}
    for pack_id in ["debug-blue","debug-coral"]:
        pack=copy.deepcopy(base)
        if pack_id=="debug-coral":
            pack["packId"]="debug-coral-v1"
            pack["defaultParts"].update(Body="body-coral",Hair="hair-b",MainHand="weapon-b")
        path=output_root/"authoring/characters/appearance"/pack_id/"appearance-pack.json"
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(pack,indent=2)+"\n")
    manifest={"status":"DEV_ONLY_ENGINE_FIXTURE","motionTemplate":str(motion_dir.relative_to(output_root)/"motion-template.json"),"appearancePacks":["authoring/characters/appearance/debug-blue/appearance-pack.json","authoring/characters/appearance/debug-coral/appearance-pack.json"],"runtimeAtlases":hashes,"productionArt":False,"roKeyPoses":0,"ownerVisualApproval":False,"registration":template["registration"]}
    path=output_root/"authoring/characters/builds/assembly-debug/build-manifest.json"
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(manifest,indent=2)+"\n")
    print("Baked",len(atlases),"debug raster atlases; two packs, one synthetic MotionTemplate")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root",type=Path,default=ROOT)
    build(parser.parse_args().output_root.resolve())
