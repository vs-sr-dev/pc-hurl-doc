# 10 — Open questions

Everything here is unresolved after the first pass, with the measurement that
raises it. Nothing in the other chapters depends on any of these answers.

## 1. What is map plane 0?

Planes 2 and 3 separate cleanly into the engine's X and Y wall grids by run
length, in every level ([04-maps.md](04-maps.md)). Plane 0 is also full of
wall indices, is balanced between horizontal and vertical runs, and is
**neither the union nor the intersection** of planes 2 and 3:

```
LEV1:  |p0| = 747   |p2| = 691   |p3| = 609
       |p2 ∪ p3| = 1162    |p2 ∩ p3| = 138
       cells in p0 but not in p2 ∪ p3 : 137
       cells in p2 ∪ p3 but not in p0 : 552
```

Where both plane 0 and plane 2 are non-zero the values agree 489 times out of
561; plane 0 against plane 3 agrees only 36 times out of 156. A plausible
reading is that plane 0 is the editor's block map and planes 2/3 are the
derived face grids, but the 137 cells that exist only in plane 0 contradict
the simple version of that.

**To resolve:** disassemble the map loader, or find an ACK-3D level editor
that writes this layout.

## 2. What were the 1040 unused bytes for?

520 `uint16` between the grids and the record count, at a fixed offset in
every file, never written by any shipped level, and in six files still holding
leftover tile values ([09](09-easter-eggs-and-leftovers.md)). 520 is not a
round number in any obvious way — it is not 4096, not 64, not a multiple of 6.

## 3. What is the `extra` field of a map record?

`{uint16 cell; uint8 value; uint16 extra;}`. `value` is demonstrably a wall
slot, and the records place shop signs and statues on individual wall faces.
`extra` is 0 in every level-specific record and non-zero only in two of the
five boilerplate records shared by all eleven files — which suggests it is
either unused, or used by something no shipped level does.

## 4. `LevelType:`, `Timer:` and `Rect:`

Three keywords Deep River added to the parser and never used. `Rect:` is
followed in the data segment by the format string `%d, %d, %d, %d`, so it took
four integers — a rectangle in map or screen coordinates. `Timer:` in a game
with no visible timer is suggestive; so is `LevelType:` in a game whose ten
levels are all the same type.

`PALFILE:` is ACK-3D's own and also unused, which is less interesting.

## 5. 1800 versus 1920

`KIT.OVL`'s seven trigonometry tables have 1800 entries per turn — 0.2° per
step, verified against `sin`, `cos`, `tan` and their reciprocals to the last
digit ([01](01-executables.md)). But every level script comments its direction
field `30=160, 45=240, 90=480, 180=960, 270=1440`, i.e. **1920** per turn, and
the values that actually occur in the files are consistent with 1920 (1440,
960, 1680, 480). `PlayerAngle` values reach 1482.

Either the object facing is in different units from the caster's angle and is
converted, or the comment is inherited from a version of the engine with a
different `INT_ANGLE_360`. The second cosine table in `KIT.OVL` chunk 1 uses a
third resolution, 4096 steps.

## 6. How is `God Mode!` triggered?

The string exists, along with `No Intro`. The switches are compared as
characters in code and no option string survives in the data segment, so this
needs a disassembly of the argument parser. The same applies to whatever
writes `pic%04d.raw`.

## 7. What sample rate are the `.SND` files?

They have no header at all — the rate is a parameter DIGPAK receives from the
caller. 11025 Hz gives plausible durations for everything (a 7.3-second toilet
flush, telephone calls of 30–90 seconds) and is the tools' default, but this
is an inference from plausibility, not a measurement. The answer is in the
`SNDSTRUC` the game fills in before calling `DigPlay`.

## 8. Which title screen does the retail game actually show?

`H.EXE` references `slobtitl.gif` and `hurl.gif` in the same intro sequence,
along with `slobad.gif`, which is not on the disc. Whether one is chosen, both
are shown in turn, or the missing file breaks the branch, needs the game
running under a debugger.

## 9. Four of the wall flag bits

Wall cells above 255 are `flags << 8 | slot`, and three of the flags are
settled by the data ([04-maps.md](04-maps.md)): `0x10` is a door, `0x40` on
top of it makes the door need a key, and `0x08` marks a see-through texture.

Four remain:

| Flag | Cells | Where it lands |
|---:|---:|---|
| `0x01` (only ever with `0x08`) | 185 | arches, black tiles, blank tiles |
| `0x02` | 173 | `wall2.gif`, `CLASS-1.GIF`, `LOCKER2/4.GIF` — ordinary opaque interior walls |
| `0x04` | 20 | `marb1a.gif` only, in one level |
| `0x20` | 23 | hedges, `LIBRARY4.GIF`, `SIDETILE.GIF`, trailer siding |

`0x02` is the awkward one: 82 of its 173 cells are `wall2.gif` in a single
level, on a texture that is not transparent, not a door and not otherwise
special.

## 10. What is the `LoadType:` value for?

Every level says `LoadType: 1`, in the wall bitmap block, and nothing varies.
ACK-3D's own keyword, so the answer is in the engine.
