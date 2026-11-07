"""Render a private pen profile and UTF-8 letter to a standalone SVG (Python 3.9+)."""
import argparse
import json
import math
import os
import sys
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET


def load_reference(path, wanted):
    found = {}
    if path and wanted:
        with path.open(encoding="utf-8") as source:
            for line in source:
                entry = json.loads(line)
                char = entry["character"]
                if char in wanted and entry.get("medians"):
                    found[char] = {"strokes": [
                        [[x * 100 / 1024, (900 - y) * 100 / 1024, 1] for x, y in run]
                        for run in entry["medians"]]}
                    if found.keys() >= wanted:
                        break
    return found


def resolve(shape, components, chain=()):
    for run in shape.get("strokes", []):
        if not run:
            raise ValueError("empty stroke")
        points = []
        for point in run:
            if len(point) not in (2, 3, 4):
                raise ValueError("expected [x,y,pressure?,corner?]")
            x, y = point[:2]
            p = point[2] if len(point) >= 3 else 1
            if not all(math.isfinite(n) for n in (x, y, p)) or p <= 0:
                raise ValueError("invalid coordinates or pressure")
            points.append((x, y, p, len(point) == 4 and bool(point[3])))
        yield points
    for part, box in shape.get("parts", []):
        if part in chain:
            raise ValueError("component cycle: " + " / ".join((*chain, part)))
        dx, dy, w, h = box
        for run in resolve(components[part], components, (*chain, part)):
            yield [(dx+x*w/100, dy+y*h/100, p, corner) for x,y,p,corner in run]


def smooth(points):
    # Cut corners gently, retaining deliberate changes of direction and pressure.
    for _ in range(2):
        result = [points[0]]
        for i in range(1, len(points)-1):
            point = points[i]
            if point[3]:
                result.append(point)
            else:
                for neighbor in (points[i-1], points[i+1]):
                    result.append(tuple(.8*a+.2*b for a,b in zip(point[:3],neighbor[:3]))+(False,))
        if len(points)>1:
            result.append(points[-1])
        points = result
    return points


def ink(group, run, width):
    points = smooth(run)
    if len(points)==1:
        x,y,p,_ = points[0]
        ET.SubElement(group,"circle",cx=str(x),cy=str(y),r=str(width*p/2))
        return
    left, right = [], []
    for i,(x,y,p,_) in enumerate(points):
        before = points[max(i-1,0)]
        after = points[min(i+1,len(points)-1)]
        dx,dy = after[0]-before[0],after[1]-before[1]
        length = math.hypot(dx,dy) or 1
        radius = width*p/2
        nx,ny = -dy*radius/length,dx*radius/length
        left.append((x+nx,y+ny))
        right.append((x-nx,y-ny))
    coords = " ".join(f"{x:.2f},{y:.2f}" for x,y in left+right[::-1])
    ET.SubElement(group,"polygon",points=coords)


def render(profile, text, reference=None):
    glyphs = dict(profile["glyphs"])
    if "" in glyphs:
        raise ValueError("empty glyph key")
    keys = sorted(glyphs, key=len, reverse=True)
    needed = set()
    tokens = []
    for line in text.expandtabs(4).split("\n"):
        row, i = [], 0
        while i < len(line):
            key = next((k for k in keys if line.startswith(k,i)),line[i])
            if key != " " and key not in glyphs:
                needed.add(key)
            row.append(key)
            i += len(key)
        tokens.append(row)
    refs = load_reference(reference,needed)
    glyphs.update(refs)
    missing = sorted(needed-refs.keys())
    if missing:
        raise ValueError("请补画这些字或提供参考骨架："+" ".join(missing))
    pen = profile.get("pen",{})
    width = float(pen.get("width",2.9))
    slant = float(pen.get("slant",0))
    if not 0 < width <= 25 or not -45 <= slant <= 45:
        raise ValueError("pen parameters out of range")
    rows, advances = [], []
    for line in tokens:
        row, x = [], 0
        for key in line:
            advance = 42 if key==" " else float(glyphs[key].get("advance",100))
            if not 0<advance<=600:
                raise ValueError("advance must be in (0,600]")
            if row and x+advance > 1500:
                rows.append(row)
                advances.append(x)
                row, x = [], 0
            row.append((x,key))
            x += advance
        rows.append(row)
        advances.append(x)
    w = max(360,max(advances)+140)
    h = 160+150*len(rows)
    page=ET.Element("svg",xmlns="http://www.w3.org/2000/svg",viewBox=f"0 0 {w} {h}",
                    width=str(round(w)),height=str(h))
    ET.SubElement(page,"title").text=text
    ET.SubElement(page,"rect",width="100%",height="100%",fill=pen.get("paper","#faf7ed"))
    counts={}
    for line_number,row in enumerate(rows):
        for x,key in row:
            if key==" ":
                continue
            base=glyphs[key]
            versions=[base]+base.get("variants",[])
            shape=versions[counts.get(key,0)%len(versions)]
            counts[key]=counts.get(key,0)+1
            runs=list(resolve(shape,profile.get("components",{})))
            if not runs:
                raise ValueError("empty glyph: "+key)
            group=ET.SubElement(page,"g",fill=pen.get("ink","#263748"),
                        transform=f"translate({70+x} {65+line_number*150}) skewX({slant})")
            for run in runs:
                ink(group,run,width)
    return ET.tostring(page,encoding="utf-8",xml_declaration=True)


EXAMPLE = Path(__file__).resolve().parent.parent / "assets" / "example.json"


def warn_copied(profile, profile_path):
    """示例字帖只是演示格式。私人字帖里如果有字跟示例一模一样，提醒一句。"""
    try:
        if profile_path.resolve() == EXAMPLE.resolve() or not EXAMPLE.exists():
            return
        example = json.loads(EXAMPLE.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return
    same = [k for k, v in profile.get("glyphs", {}).items() if example.get("glyphs", {}).get(k) == v]
    same += [k for k, v in profile.get("components", {}).items() if example.get("components", {}).get(k) == v]
    if same:
        print("提醒：这些字形跟示例字帖一模一样：" + "、".join(same)
              + "。示例只是演示格式，请画你自己的。", file=sys.stderr)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile",type=Path)
    parser.add_argument("letter",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--reference",type=Path)
    args=parser.parse_args()
    if args.output.resolve() in {p.resolve() for p in [args.profile,args.letter,args.reference] if p}:
        parser.error("output must differ from inputs")
    try:
        profile=json.loads(args.profile.read_text(encoding="utf-8-sig"))
        warn_copied(profile,args.profile)
        content=args.letter.read_text(encoding="utf-8-sig").rstrip("\n")
        if not content.strip():
            raise ValueError("empty letter")
        svg=render(profile,content,args.reference)
    except (ValueError,KeyError,TypeError,OSError) as e:
        parser.exit(1,f"{e}\n")
    with tempfile.NamedTemporaryFile(dir=args.output.parent,delete=False) as temp:
        tmp=Path(temp.name)
        try:
            temp.write(svg)
            temp.close()
            os.replace(tmp,args.output)
        finally:
            tmp.unlink(missing_ok=True)

if __name__=="__main__":
    main()
