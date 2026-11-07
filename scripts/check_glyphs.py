"""对着笔顺骨架，查字帖里亲手画的字结构对不对（Python 3.9+，只用标准库）。

只查结构，不管好不好看：笔画数对不对，每一笔从哪起、到哪停，跟参考差多远。
凭记忆画字很容易多一横、少一点、竖画出头，这个工具就是用来提前拦住这些的。

    python scripts/check_glyphs.py 字帖.json --reference graphics.txt
    python scripts/check_glyphs.py 字帖.json --reference graphics.txt --chars 黑天

参考文件每行一个 JSON：{"character":"某","medians":[[[x,y],...],...]}，
即 Make Me a Hanzi 的 graphics.txt 格式（需另行下载，遵守其许可）。
"""
import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_letter import load_reference, resolve  # noqa: E402


def normalize(runs):
    """按整字的外框缩放到 0..1，免得字大字小、偏左偏右影响比较。"""
    xs = [p[0] for r in runs for p in r]
    ys = [p[1] for r in runs for p in r]
    x0, y0 = min(xs), min(ys)
    w, h = max(max(xs) - x0, 1e-6), max(max(ys) - y0, 1e-6)
    return [[((p[0] - x0) / w, (p[1] - y0) / h) for p in r] for r in runs]


def compare(mine, ref, tol):
    problems = []
    if len(mine) != len(ref):
        problems.append(f"笔画数：你画了 {len(mine)} 笔，参考是 {len(ref)} 笔")
    a, b = normalize(mine), normalize(ref)
    for i, (m, r) in enumerate(zip(a, b), 1):
        ds, de = math.dist(m[0], r[0]), math.dist(m[-1], r[-1])
        if ds > tol or de > tol:
            problems.append(
                f"第 {i} 笔：起点差 {ds:.2f}，终点差 {de:.2f}"
                f"（你 {m[0][0]:.2f},{m[0][1]:.2f}→{m[-1][0]:.2f},{m[-1][1]:.2f}；"
                f"参考 {r[0][0]:.2f},{r[0][1]:.2f}→{r[-1][0]:.2f},{r[-1][1]:.2f}）")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profile", type=Path)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--chars", default="", help="只查这些字；不填就查字帖里所有单字")
    ap.add_argument("--tol", type=float, default=0.22, help="起止点允许差多少（0..1，默认 0.22）")
    args = ap.parse_args()

    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    comps = profile.get("components", {})
    glyphs = profile.get("glyphs", {})
    keys = [k for k in (args.chars or glyphs) if len(k) == 1 and k in glyphs and k.isalpha()]
    ref = load_reference(args.reference, set(keys))

    checked = bad = 0
    for ch in keys:
        if ch not in ref:
            print(f"{ch}  参考里没有，跳过")
            continue
        shapes = [glyphs[ch]] + glyphs[ch].get("variants", [])
        for vi, shape in enumerate(shapes):
            mine = [[(x, y) for x, y, *_ in run] for run in resolve(shape, comps)]
            refr = [[(x, y) for x, y, *_ in run] for run in ref[ch]["strokes"]]
            probs = compare(mine, refr, args.tol)
            checked += 1
            name = ch if vi == 0 else f"{ch}（变体 {vi}）"
            if probs:
                bad += 1
                print(f"{name}  ✗")
                for p in probs:
                    print("    " + p)
    print(f"查了 {checked} 个字形，{bad} 个要再看一眼。")
    print("提示：起止点有差别不一定是错，可能只是你的写法；笔画数不对多半是真错了。")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
