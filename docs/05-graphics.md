# 05 — Graphics

H.U.R.L. does not have a picture format. It has three, and all three are
off-the-shelf: **GIF87a** for every tile and sprite, **IFF `PBM `** (Deluxe
Paint II Enhanced) for full-screen backdrops and the font, and a standard
Autodesk **FLI** for the one animation. The artists' files went into the
archives untouched, extension and all.

```sh
python tools/hurlgfx.py "<install>" palettes
python tools/hurlgfx.py "<install>" png   LEV1 out/lev1
python tools/hurlgfx.py "<install>" sheet LEV1 out/lev1.png
python tools/hurlgfx.py "<install>" res   GRAPH out/graph
python tools/hurlgfx.py "<install>" font  out/font.png
python tools/hurlgfx.py "<install>" fli   frames out/mlogo
```

## GIF87a — every wall and every sprite

All 2,762 image chunks in the level containers are GIF87a, and every single
one is **64 × 64** with a 256-entry global colour table. There is no
sprite sheet, no compiled-shape format and no run-length scheme of the game's
own: a wall texture and a walking pig frame are the same thing, an LZW-coded
GIF, and the engine decodes GIF at load time. The `GIF` signature check is
still in `H.EXE` at `0x2b2e7`.

Menus and cutscenes are GIF too, at their natural sizes: 320×200 for full
screens, 320×160 for the phone panels, and small odd sizes for HUD pieces —
20×7 for the ammo counters, 28×28 for the keys, 91×27 for the buttons.

684 of the 2,762 tile images are distinct; the other 75% are per-level copies
([02-containers.md](02-containers.md)).

## One palette for the whole game

Sixteen distinct 256-colour tables exist across the disc, but one of them
covers **2,739 of the ~2,850 images**, and it is a designed artist's palette,
not a quantiser's output:

```
index   0        black
index   1.. 15   a 15-step grey ramp, 252,252,252 down to 12,12,12
index  16..254   fifteen further 16-step ramps, each bright to dark
index 255        white
```

Every band is monotonically descending in all three channels — sixteen hue
ramps of sixteen, with black and white pinned at the ends. This is what you
get from Deluxe Paint's "make a range" tool, used sixteen times.

Two consequences show up elsewhere in the data:

* The `TopColor:` and `BottomColor:` values in the level scripts are indices
  into it. `TopColor: 174` is `(21, 38, 64)`, a dark blue sky; `BottomColor:
  12` is `(63, 63, 63)` road grey, `108` is `(25, 97, 25)` grass green, `90`
  is `(72, 134, 31)` a lighter green — and `LEV10` alone uses `200`, which is
  `(97, 49, 174)`, **purple**.
* The colour-cycle ranges Deluxe Paint left in `KIT.OVL` — `0x10`–`0x1F`,
  `0x20`–`0x2F`, `0x60`–`0x6F`, `0x90`–`0x9F` — line up exactly with four of
  the sixteen bands.

The GIF art and the Deluxe Paint art share this palette **byte for byte**: the
global colour table of a level's tiles and the `CMAP` of its `ScreenBack`
picture are the same 768 bytes. Whatever converted the artwork between the two
formats did not requantise.

The remaining fifteen palettes belong to the cutscenes (`CUT.RES`, one shared
palette for all ten cards), the intro sequence, and a handful of one-off menu
pictures.

## IFF `PBM ` — the backdrops and the font

`FORM …… PBM ` with `BMHD`, `CMAP` and `BODY`, ByteRun1-compressed, eight
bitplanes, 320 × 200 with a 320 × 200 page size. The engine's loader has its
own error string for this: `Error: Not form PBM!`, and `ERR_NOPBM` in the
error table.

Two per level:

* **chunk 2, `ScreenBack`** — the HUD frame: a green slime border with
  `DIRT`, `MONEY` and `SCORE` gauges along the bottom and three ammunition
  slots, with the middle left black for the 3-D view. It is **byte-identical
  in all eleven level files**.
* **chunk 3, `ScrollBack`** — the horizon: a band of pine trees and clouds,
  stored twice stacked inside the 320 × 200 frame so it can wrap horizontally
  without a seam. Only **three distinct skies** exist, shared as
  {LEV1, LEV5, LEV8}, {LEV6, LEV10} and {LEV2, LEV3, LEV4, LEV7, LEV9, PICS}.

The third `PBM ` on the disc is the font in `KIT.OVL`, 294 × 5, described in
[01-executables.md](01-executables.md).

### What Deluxe Paint left behind

The font chunk still carries three chunks that only the paint program cared
about, and that nothing in the game reads:

| Chunk | Contents |
|---|---|
| `GRAB` | hotspot at (147, 2) — the centre of the strip |
| `TINY` | a 120-byte thumbnail |
| `CRNG` × 16 | sixteen colour-cycle range definitions, four of them filled in, all with rate 0 and flags 0 (i.e. defined but not cycling) |

The level backdrops were saved without them, so somewhere in the pipeline the
files went through two different export paths.

## `MLOGO.FLI`

One 233,149-byte Autodesk FLI: magic `0xAF11`, 320 × 200, 8-bit, **137
frames** at speed 6 (6/70 s per frame, ≈ 11.7 fps, so about 11.7 seconds).
The header's size field matches the file exactly. It animates the Millennium
Media Group logo over a starfield, and it is the only moving picture in the
game — every other "animation" is a bitmap list in a level script.

`H.EXE` has `fli read error` and `Cannot open %s` for it, and plays
`mlogo.xmi` underneath.
