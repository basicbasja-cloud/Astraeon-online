#!/usr/bin/env python3
"""Inspect private ACT/SPR inputs; emit numeric metadata, never sprite imagery.

No animation phase, anatomical socket, action name or sword variant is inferred.
The caller must identify lawful local inputs and the client/timing profile.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

DIRECTIONS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]


class Reader:
    def __init__(self, data: bytes):
        self.data, self.offset = data, 0

    def take(self, size: int) -> bytes:
        if size < 0 or self.offset + size > len(self.data):
            raise ValueError(f"Truncated reference at byte {self.offset}, need {size}")
        out = self.data[self.offset:self.offset+size]
        self.offset += size
        return out

    def unpack(self, fmt: str):
        return struct.unpack("<" + fmt, self.take(struct.calcsize("<" + fmt)))

    def count(self, fmt: str = "I", limit: int = 10000) -> int:
        n, = self.unpack(fmt)
        if n > limit:
            raise ValueError(f"Reference count {n} exceeds inspection bound {limit}")
        return n

    def finite(self) -> float:
        value, = self.unpack("f")
        if not math.isfinite(value):
            raise ValueError("Nonfinite reference transform/timing")
        return value


def inspect_act(data: bytes, tick_ms: int) -> dict:
    if tick_ms not in (24, 25):
        raise ValueError("Choose explicit 24 or 25 ms ACT timing profile")
    r = Reader(data)
    if r.take(2) != b"AC":
        raise ValueError("Expected AC signature")
    minor, major = r.unpack("BB")
    if major != 2 or minor not in range(6):
        raise ValueError(f"Unsupported ACT {major}.{minor}; no default decoding")
    count = r.count("H", 1024)
    r.take(10)
    actions = []
    for ai in range(count):
        frames = []
        for fi in range(r.count()):
            r.take(32)
            layers = []
            for li in range(r.count(limit=512)):
                x, y, index, flags = r.unpack("iiii")
                tint = list(r.unpack("BBBB"))
                sx = r.finite()
                sy = r.finite() if minor >= 4 else sx
                rotation, image_type = r.unpack("ii")
                dimensions = list(r.unpack("ii")) if minor >= 5 else None
                layers.append({"layerIndex": li, "x": x, "y": y,
                               "imageIndex": index, "mirrorFlag": flags,
                               "tintRGBA": tint, "scale": [sx, sy],
                               "rotationDegrees": rotation, "imageType": image_type,
                               "imageDimensions": dimensions})
            event, = r.unpack("i")
            anchors = []
            if minor >= 3:
                for pi in range(r.count(limit=128)):
                    unknown, x, y, attribute = r.unpack("iiii")
                    anchors.append({"index": pi, "x": x, "y": y,
                                    "unknown": unknown, "attribute": attribute})
            frames.append({"sourceFrameIndex": fi, "layers": layers,
                           "eventIndex": event, "actAnchors": anchors,
                           "referencePhase": None, "anatomicalAnchors": None})
        actions.append({"actionId": ai, "candidateGroup": ai//8,
                        "candidateDirection": DIRECTIONS[ai % 8],
                        "frameCount": len(frames), "rawInterval": None,
                        "durationMs": None, "frames": frames})
    events = []
    if minor >= 1:
        for _ in range(r.count(limit=4096)):
            events.append(r.take(40).split(b"\0", 1)[0].decode("euc-kr", "replace"))
        if minor >= 2:
            for action in actions:
                interval = r.finite()
                if interval <= 0:
                    raise ValueError("Nonpositive ACT interval; annotate unsupported timing explicitly")
                action["rawInterval"] = interval
                action["frameDelayMs"] = interval*tick_ms
                action["durationMs"] = len(action["frames"])*interval*tick_ms
    if r.offset != len(data):
        raise ValueError(f"Unparsed ACT trailing bytes: {len(data)-r.offset}")
    return {"format": "ACT", "version": f"{major}.{minor}",
            "sha256": hashlib.sha256(data).hexdigest(), "msPerInterval": tick_ms,
            "classification": "SOURCE-DERIVED_NUMERIC_METADATA",
            "actionNamesEstablished": False, "poseIntentEstablished": False,
            "events": events, "actions": actions}


def inspect_spr(data: bytes) -> dict:
    r = Reader(data)
    if r.take(2) != b"SP":
        raise ValueError("Expected SP signature")
    minor, major = r.unpack("BB")
    if (major, minor) not in ((1, 0), (1, 1), (2, 0), (2, 1)):
        raise ValueError(f"Unsupported SPR {major}.{minor}")
    indexed_count = r.count("H")
    rgba_count = r.count("H") if major >= 2 else 0
    images = []
    for i in range(indexed_count):
        width, height = r.unpack("HH")
        encoded_size = r.count("H", 65535) if (major, minor) >= (2, 1) else width*height
        r.take(encoded_size)
        images.append({"index": i, "type": "indexed", "width": width, "height": height})
    for i in range(rgba_count):
        width, height = r.unpack("HH")
        r.take(width*height*4)
        images.append({"index": i, "type": "ABGR", "width": width, "height": height})
    if indexed_count and (major, minor) >= (1, 1):
        r.take(1024)
    if r.offset != len(data):
        raise ValueError(f"Unparsed SPR trailing bytes: {len(data)-r.offset}")
    return {"format": "SPR", "version": f"{major}.{minor}",
            "sha256": hashlib.sha256(data).hexdigest(), "images": images,
            "classification": "SOURCE-DERIVED_DIMENSIONS_ONLY", "pixelsExported": False}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--act", action="append", required=True, metavar="COMPONENT=PRIVATE_PATH")
    ap.add_argument("--spr", action="append", default=[], metavar="COMPONENT=PRIVATE_PATH")
    ap.add_argument("--tick-ms", type=int, choices=[24, 25], required=True)
    ap.add_argument("--client-build", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    components = {}
    for kind, items in (("act", args.act), ("spr", args.spr)):
        for item in items:
            name, path = item.split("=", 1)
            if not name or kind in components.setdefault(name, {}):
                raise ValueError("Empty or duplicate component reference")
            data = Path(path).read_bytes()
            components[name][kind] = inspect_act(data, args.tick_ms) if kind == "act" else inspect_spr(data)
    result = {"schemaVersion": "1.0", "clientBuild": args.client_build,
              "referencePolicy": "PRIVATE INPUTS; DERIVED METADATA ONLY; NO RUNTIME DEPENDENCY",
              "productionMotionReady": False, "components": components,
              "remaining": ["Verify job/weapon action mapping", "Inspect composed keys locally",
                            "Annotate key poses, foot contacts and anatomical anchors",
                            "Review ACT/SPR-specific direction and layer ordering"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
