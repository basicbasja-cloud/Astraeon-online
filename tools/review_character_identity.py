#!/usr/bin/env python3
"""Verify preserved ASTRAEON neutral candidates and make review-only comparisons.

Does not generate, repaint, split, approve or install any production artwork.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/review/character-ro1-engine-v1/identity"
DIRECTIONS=["S","SW","W","NW","N","NE","E","SE"]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    authority=ROOT/"authoring/characters/gait-rig-v50/approved-warrior-seed.png"
    expected="750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05"
    assert hashlib.sha256(authority.read_bytes()).hexdigest()==expected
    seed=Image.open(authority).convert("RGBA")
    source=ROOT/"authoring/characters/swordsman-production"
    registration=json.loads((source/"reference/master-registration.json").read_text())
    provenance=json.loads((source/"candidates/directional-02/provenance.json").read_text())
    records=[];masters=[]
    for direction in DIRECTIONS:
        path=source/"masters"/(direction+".png")
        image=Image.open(path)
        assert image.mode=="RGBA" and image.size==(320,320)
        alpha=image.getchannel("A")
        edge=max(alpha.crop((0,0,320,1)).getextrema()[1],alpha.crop((0,319,320,320)).getextrema()[1],alpha.crop((0,0,1,320)).getextrema()[1],alpha.crop((319,0,320,320)).getextrema()[1])
        assert edge==0, direction+" clipped candidate"
        records.append({"direction":direction,"path":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"canvas":[320,320],"alphaBounds":list(alpha.getbbox()),"root":registration["canonicalRoot"],"edgeAlphaMax":edge,"structuralStatus":"PASS","visualStatus":"REQUIRES_OWNER_VISUAL_REVIEW"})
        masters.append((direction,image))
    for scale,label in [(70/176,"gameplay-1x"),(140/176,"review-2x"),(1,"diagnostic")]:
        tile=max(140,round(320*scale)+20);height=round(320*scale)+50
        sheet=Image.new("RGB",(tile*5,height*2+60),"#23303d");draw=ImageDraw.Draw(sheet)
        draw.text((10,10),"ASTRAEON identity only — preserved seed + historical generated neutral candidates",fill="white")
        draw.text((10,30),"REQUIRES_OWNER_VISUAL_REVIEW — no new motion/art approval",fill="#ffcf6c")
        for i,(name,im) in enumerate([("IDENTITY SEED",seed),*masters]):
            x=(i%5)*tile;y=(i//5)*height+60
            draw.text((x+8,y+5),name,fill="white")
            painted=im.resize((round(320*scale),round(320*scale)),Image.Resampling.LANCZOS)
            sheet.paste(painted,(x+(tile-painted.width)//2,y+25),painted)
            rootx=x+(tile-painted.width)//2+round(160*scale);rooty=y+25+round(264*scale)
            draw.line((rootx-5,rooty,rootx+5,rooty),fill="#fd7e8c",width=1)
        sheet.save(OUT/(label+".png"))
    report={"identityAuthority":authority.relative_to(ROOT).as_posix(),"seedSHA256":expected,"approvalProvenance":"Historical repository README/identity-lock; no new approval inferred","candidateSource":"first-party directional-02 generated edit; not owner-supplied by provenance","candidateOwnerApproval":False,"cameraAndRootConvention":registration,"neutralTurnaroundStructuralStatus":"PASS_PRESERVED_CANDIDATE","neutralTurnaroundVisualStatus":"REQUIRES_OWNER_VISUAL_REVIEW","productionAnimationAuthorizedByThisReport":False,"candidateNotes":["Eight complete alpha canvases and shared normalization established structurally","Same-person, camera, hair, costume, sword dimensions and handedness still require owner visual review","Do not derive new modular layers by subtracting the flattened candidate"],"directions":records}
    (OUT/"identity-review.json").write_text(json.dumps(report,indent=2)+"\n")
    target=ROOT/"authoring/characters/appearance/bodies/swordsman-male-default"
    target.mkdir(parents=True,exist_ok=True)
    (target/"identity-source.json").write_text(json.dumps({"status":"REQUIRES_OWNER_VISUAL_REVIEW","productionBodySpriteSetReady":False,"reference":report["identityAuthority"],"referenceSHA256":expected,"turnaroundReview":"docs/review/character-ro1-engine-v1/identity/identity-review.json","sourcePolicy":"Identity reference only; no procedural art and no flattened-character subtraction as new modular source"},indent=2)+"\n")
    print("Preserved eight-direction identity candidate: structural PASS; owner approval pending")


if __name__=="__main__":main()
