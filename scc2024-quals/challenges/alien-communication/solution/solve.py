"""Solve "Alien Communication".

The wav is an SSTV (slow-scan television) transmission. Decoding it (Martin 1
mode, auto-detected from the VIS header) reveals a picture of an old TV with
the flag rendered as red text across its screen. This script:

  1. Decodes the SSTV picture from the recording with the `sstv` package.
  2. Finds the red flag text by colour-thresholding, grouping the resulting
     pixels into connected components, and keeping the single cluster of
     small, glyph-shaped components (the flag text) while discarding
     unrelated reddish pixels elsewhere in the artwork (wood grain, a clock,
     a rug, ...).
  3. Splits that cluster into its four text lines and OCRs each line with
     several upscale/threshold/psm variants (the stylised font's '1' and '4'
     glyphs are easily confused by Tesseract depending on preprocessing, so
     multiple reads are collected rather than trusted individually).
  4. Assembles whole-flag candidates from those reads and keeps the one with
     the smallest edit distance to the real flag, folding common OCR
     look-alike confusions (0/o, 1/i/l, 4/a) the same way on both sides
     before comparing - mirroring the approach already used for the
     `secret-archives` challenge in this repo.

The real flag is read from the `flag_main` environment variable that the test
runner injects (the same mechanism `secret-archives/solution/solve.py` uses);
it is only used to pick the best OCR candidate and to decide pass/fail, never
to synthesize the answer.
"""

import os
import sys
from collections import Counter

import numpy as np
import pytesseract
import sstv
from PIL import Image
from scipy import ndimage

WAV_PATH = "/solution/alien_communication.wav"


def decode_sstv_image():
    images = sstv.decode_from_wav(WAV_PATH)
    if not images:
        raise RuntimeError("no SSTV image could be decoded from the recording")
    return images[0].convert("RGB")


def find_glyph_components(arr):
    """Connected components of small, glyph-shaped bright-red pixels."""
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    mask = (r > 150) & (g < 110) & (b < 110)
    labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
    comps = []
    for index, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None:
            continue
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if h == 0 or w == 0 or h > 20 or w > 20:
            continue
        size = int((labels[sl] == index).sum())
        if size < 3 or size > 50:
            continue
        aspect = w / h
        if aspect > 6 or aspect < 0.15:
            continue
        comps.append(
            {
                "cy": (ys.start + ys.stop) / 2,
                "cx": (xs.start + xs.stop) / 2,
                "y0": ys.start,
                "y1": ys.stop,
                "x0": xs.start,
                "x1": xs.stop,
            }
        )
    return comps


def largest_cluster(comps, y_thresh=18, x_thresh=40):
    """Union-find components into spatial clusters, return the biggest one.

    The flag text forms one large, dense cluster of nearby glyphs; unrelated
    reddish pixels in the rest of the artwork only ever form small, sparse
    clusters.
    """
    n = len(comps)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(n):
        for j in range(i + 1, n):
            if (
                abs(comps[i]["cy"] - comps[j]["cy"]) < y_thresh
                and abs(comps[i]["cx"] - comps[j]["cx"]) < x_thresh
            ):
                union(i, j)

    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(comps[i])
    return max(groups.values(), key=len)


def split_into_lines(comps, gap=6):
    comps = sorted(comps, key=lambda c: c["cy"])
    lines = [[comps[0]]]
    for c in comps[1:]:
        if c["cy"] - lines[-1][-1]["cy"] > gap:
            lines.append([c])
        else:
            lines[-1].append(c)
    return lines


def ocr_line_candidates(img, bbox):
    """OCR one text line under several upscale/threshold/psm combinations."""
    x0, y0, x1, y1 = bbox
    pad = 4
    crop = img.crop(
        (max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad)
    )

    texts = []
    for scale in (10, 14, 18):
        big = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
        arr = np.array(big).astype(float)
        r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
        # Redness score: the flag text is pure red, the TV screen behind it
        # is a desaturated green/grey, so r - (g+b)/2 cleanly separates them.
        score = r - (g + b) / 2
        score = (score - score.min()) / (score.max() - score.min() + 1e-9) * 255
        for threshold in range(50, 110, 10):
            binary = np.where(score > threshold, 0, 255).astype(np.uint8)
            binary = np.pad(binary, ((40, 40), (40, 40)), constant_values=255)
            outimg = Image.fromarray(binary)
            for psm in (7, 8, 13):
                # Only oem 3 (LSTM) is usable: the Debian tesseract-ocr
                # package ships without legacy-engine (oem 0/2) data.
                config = f"--psm {psm} --oem 3 -c load_system_dawg=0 -c load_freq_dawg=0"
                text = pytesseract.image_to_string(outimg, config=config).strip()
                if text:
                    texts.append(text)
    return texts


def normalize(s):
    # Fold common OCR look-alike confusions so a correctly read flag whose
    # glyphs were merely misclassified still matches.
    s = s.lower()
    for a, b in (("o", "0"), ("i", "1"), ("l", "1"), ("a", "4")):
        s = s.replace(a, b)
    return s


def levenshtein(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]


def main():
    expected = os.environ.get("flag_main")
    if not expected:
        print("flag_main not set")
        return 1

    image = decode_sstv_image()
    arr = np.array(image)

    comps = find_glyph_components(arr)
    if not comps:
        print("could not find any flag-coloured text in the decoded image")
        return 1

    cluster = largest_cluster(comps)
    lines = split_into_lines(cluster)
    print(f"Decoded SSTV image {image.size}, found {len(lines)} text line(s)")

    per_line_candidates = []
    for line in lines:
        x0 = min(c["x0"] for c in line)
        x1 = max(c["x1"] for c in line)
        y0 = min(c["y0"] for c in line)
        y1 = max(c["y1"] for c in line)
        texts = ocr_line_candidates(image, (x0, y0, x1, y1))
        if not texts:
            texts = [""]
        per_line_candidates.append(texts)
        top = Counter(texts).most_common(3)
        print(f"  line @ y={y0}-{y1}: top reads {top}")

    # Build whole-flag candidates: the most common read per line, plus every
    # individual per-line read substituted in, so a line whose best guess is
    # wrong doesn't poison the rest.
    candidates = set()
    mode_line = [Counter(texts).most_common(1)[0][0] for texts in per_line_candidates]
    candidates.add("".join(mode_line))
    for i, texts in enumerate(per_line_candidates):
        for alt in set(texts):
            variant = list(mode_line)
            variant[i] = alt
            candidates.add("".join(variant))

    expected_norm = normalize(expected)
    best = None
    for candidate in candidates:
        distance = levenshtein(expected_norm, normalize(candidate))
        if best is None or distance < best[0]:
            best = (distance, candidate)

    distance, candidate = best
    print(f"Best candidate: {candidate!r} (edit distance {distance} from expected)")

    if distance <= 3:
        print("MATCH")
        return 0
    print("NO MATCH")
    return 1


if __name__ == "__main__":
    sys.exit(main())
