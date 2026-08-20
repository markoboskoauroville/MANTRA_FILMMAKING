#!/usr/bin/env python3
"""Paint the plates for the field book. One style paragraph, varied only by scene."""
import json, base64, os, sys, time, urllib.request

KEY = open('/home/claude/.secret/gemini_key').read().strip()
URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
       "gemini-3-pro-image-preview:generateContent")
OUT = '/home/claude/MANTRA_FILMMAKING/images'

STYLE = (
    "Dark moody watercolour on textured paper, in the manner of a nocturne. "
    "One warm amber light source glowing from inside the composition; everything else "
    "deep umber, warm black and soft indigo shadow. Loose wet brushwork, visible paper "
    "grain, soft bleeding edges. Silhouettes and suggestion rather than detail. "
    "Intimate, quiet, hand-painted. The painting fills the entire frame edge to edge "
    "with no white paper border, no margin and no mount. "
    "Absolutely no text, no letters, no words, no numbers, no symbols, no interface "
    "elements and no signature anywhere in the image. SCENE: "
)

SCENES = {
 "00_hero": "a single blank sheet of drawing paper lying on a dark wooden desk, warm amber light falling across it from one side",
 "01_sentence": "one single horizontal line of dark ink drawn across a pale sheet of paper on a dark desk, one amber lamp above it",
 "02_marks": "two short strips of pale tape forming a cross on a dark studio floor, one warm amber light falling directly on them",
 "03_stool": "a single empty wooden stool standing in a dark studio in front of a plain dark backdrop, one warm amber light on it",
 "04_doors": "five closed doors along one side of a dark corridor, warm amber light showing in the gap under each door",
 "05_clock": "an hourglass standing on a dark table with almost all the sand run through, one amber lamp glowing behind it",
 "06_layers": "a photographic print resting on top of a sheet of drawing paper on a dark desk, casting a soft real shadow onto the page, one amber lamp",
 "07_glass": "a magnifying glass lying on a dark wooden surface, warm amber light bending and focusing through its lens onto the wood below",
 "08_desk": "a desk covered with spread papers in front of a dark window showing night outside, one amber lamp at the edge",
 "09_speaker": "a single studio monitor speaker standing on a stand in a dark empty room, one amber lamp low beside it",
 "10_frames": "many small blank drawn panels pinned in a grid on a dark board, warm amber light raking across them from one side",
 "11_ledger": "a large open ledger book lying on a dark desk with a pen laid across the open page, one amber lamp above",
 "12_door": "a heavy wooden door standing slightly ajar with warm amber light spilling through the gap into a dark corridor",
}

def paint(name, scene, retries=3):
    body = json.dumps({
        "contents": [{"parts": [{"text": STYLE + scene}]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": "16:9"}},
    }).encode()
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=body, headers={
            "x-goog-api-key": KEY, "Content-Type": "application/json",
            "User-Agent": "mantra-field-books/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            code = e.code
            if code == 429:                      # valid key, throttled — rest it
                time.sleep(20 * (attempt + 1)); continue
            print(f"  {name}: HTTP {code}"); return False
        for p in d["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                raw = base64.b64decode(p["inlineData"]["data"])
                open(f"{OUT}/{name}.jpg", "wb").write(raw)
                print(f"  {name}: {len(raw)//1024} KB")
                return True
        print(f"  {name}: no image part returned"); time.sleep(5)
    return False

if __name__ == "__main__":
    want = sys.argv[1:] or list(SCENES)
    ok = 0
    for n in want:
        if os.path.exists(f"{OUT}/{n}.jpg"):
            print(f"  {n}: already painted, skipping"); ok += 1; continue
        if paint(n, SCENES[n]): ok += 1
        time.sleep(2)
    print(f"painted {ok}/{len(want)}")
