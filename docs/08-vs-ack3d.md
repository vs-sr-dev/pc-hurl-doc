# 08 — What is ACK-3D and what is Deep River

H.U.R.L. is an **ACK-3D** game. ACK-3D — the Animation Construction Kit — is
Lary Myers' tile-based ray-caster, published with source in *The Amazing 3-D
Games Adventure Set* (Coriolis Group, 1995) and licensed for commercial use.
Myers is credited on the game's own credits screen as "3D Graphics".

This chapter separates the engine from the game, using only what is in the
shipped files.

## Where this engine sits

ACK-3D is the root of a family that outlived it by twenty years:

| Year | Engine |
|---|---|
| 1993 | **ACK-3D**, Lary Myers — the Wolfenstein-like open-source engine; a Linux port followed in 1994 |
| 1994 | ACK NEXT GENERATION, Johann Christian Lotter / oP Group — an improved fork |
| 1995 | ACKNEX-2, written for the German TV show *X-BASE*; acquired by Conitec and released as **3D GameStudio** |
| 1997– | ACKNEX-3, then A4 (1999), A5, A6, A7, A8 (2010) |

H.U.R.L. is on the **original 1993 Myers engine**, not the Lotter fork and not
ACKNEX: everything the binary names — `ACKVIEW.C`, `ACKPOV.C`, `ACKLDBMP.C`,
the `ERR_*` table, `trig.dat` — belongs to ACK-3D proper. It is a commercial
shipped title sitting on the first rung of the ladder that ends at 3D
GameStudio.

## The fingerprints

Everything below is a literal string in `H.EXE`:

| Evidence | Where |
|---|---|
| `ACKVIEW.C`, `ACKPOV.C`, `ACKLDBMP.C` | assertion messages |
| `ERR_BADMAPFILE`, `ERR_NOPBM`, `ERR_TOMANYVIEWS`, 18 more | the engine's error-name table |
| `Screw up in XRAY$`, `Screw up in YRAY$` | panic strings from the assembly caster |
| `Screw up in XRAYMULTI$`, `Screw up in YRAYMULTI$` | the multi-height variants |
| `Xwall %d hit`, `Ywall %d hit`, `Door %d hit`, `Object %d hit` | the engine's debug trace |
| `MoveObjectList`, `ObjectsSeen`, `MoveObjectCount` | engine array names, in assertions |
| `trig.dat` | the trig-table file ACK-3D loads by name |
| `Error: Not form PBM!` | the engine's Deluxe Paint loader |

The `$`-terminated panic strings are DOS `INT 21h/09h` message format — they
are printed from assembly, not from C.

## What came across unchanged

**The level description language.** Every keyword in the shipped `.INF` files
that is stored *upper case* in the binary is ACK-3D's:

```
MAPFILE  PALFILE  XPLAYER  YPLAYER  PLAYERANGLE  SCREENBACK  SCROLLBACK
TOPCOLOR  BOTTOMCOLOR  SHADING  FLOORS  RESOLUTION  LOADTYPE
WALLS  ENDWALLS  OBJECTS  ENDOBJECTS  BITMAPS  ENDBITMAPS  OBJDESC  ENDDESC  END
NUMBER  CREATE  DESTROY  WALK  ATTACK  INTERACT
ANIMATE  MOVEABLE  PASSABLE  MULTIVIEW  SHOWONCE
```

**The object model**: five states per object, each `flags, views,
bitmaps-per-view, list`; eight rotation views for `MULTIVIEW`; a bitmap list
walked one entry per tick.

**The map model**: a 64 × 64 grid at 64 units per cell, a combined map grid
plus separate X and Y wall grids, an object grid, floor and ceiling grids, and
wall flag bits for doors, see-through walls and multi-height walls
([04-maps.md](04-maps.md)). `AckReadMapFile` is at `0x1c270` and reads them in
one run of six `fread` calls.

**The trig tables**: seven tables of 1800 `int32` at 0.2° per step, poles
clamped to `INT32_MAX` ([01-executables.md](01-executables.md)) — and the
whole engine works in those 1800 units.

**The object bookkeeping**: `ObjectsSeen[]` at `0x3ab8c` with its count at
`0x424d0` and its 255 sentinel, exactly as the retail build's own assertion
strings describe it.

**The picture loader**: Deluxe Paint IFF `PBM `, with ACK-3D's own error codes.

## What Deep River added

**Eleven keywords**, stored mixed-case and inserted as one contiguous block in
the middle of the engine's own string table, at `0x2a4d8`–`0x2a53c`:

| Keyword | What it names | Used? |
|---|---|---|
| `RedDoor:` `GreenDoor:` `BlueDoor:` | the wall slot for each locked door | all 11 levels |
| `Vend:` | the vending machine wall | all 11 |
| `Exit:` | the exit sign wall | all 11 |
| `Shower:` | the shower wall | all 11 |
| `Phone:` | the telephone wall | all 11 |
| `Hitgrid:` | a **floor** tile that costs you two points of damage | 5 levels |
| `LevelType:` | a number, stored and never read by any level | **never** |
| `Timer:` | a number, stored and never read by any level | **never** |
| `Rect:` | four integers forming a box the object list is tested against | **never** |

All but `Hitgrid:` name a *wall*, not an object — the game's interactive
furniture is implemented as special wall indices the engine is told about up
front, which is how you add doors, phones and showers to a caster that has no
concept of any of them. `Hitgrid:` is the exception: it is compared against
the **floor** grid, and the check sits directly behind the god-mode test.

**A second cosine table** at a different resolution: 4096 steps per turn,
`cos × 16384`, in `KIT.OVL` chunk 1, alongside the engine's 1800-step tables.

**GIF as the tile format.** ACK-3D's own art path is the Deluxe Paint `PBM `
loader, which survives here for the two full-screen backdrops per level. Every
tile and sprite is GIF87a instead, decoded at load time — 2,762 of them across
the eleven containers.

**The `.DTF` container.** ACK-3D reads a `.MAP` file and loose bitmaps; here
the script, the map, the backdrops and every tile are one indexed file, and
the script refers to art by chunk index rather than by file name. The `.RES`
/`.TAB` archive is the same idea for everything outside a level.

**Everything the game is about**: money and dirt gauges, ten telephone calls,
trash with prices, the raincoat/umbrella/towelette defences, the vending
machine, the shower, and Bob.

## What the engine could do and the game never does

* `Shading: OFF` in all eleven levels — distance shading is never enabled.
* `PALFILE:` is never used, so the palette always comes from the pictures.
* `Resolution: 2` in all eleven — the other settings are never exercised.
* `LevelType:`, `Timer:` and `Rect:` are parsed, stored, and in `Rect:`'s case
  read back by a working bounding-box test — and never written by a level.
* Wall flag `0x80` and the `0x8000` branch in both casters: no cell in the
  game sets it.

**The multi-height path, by contrast, *is* used** — sparingly. `XRAYMULTI` and
`YRAYMULTI` only consider cells whose value has `0x02` or `0x04` set, and the
shipped maps flag 25 such cells in level 8 (lockers and classroom walls) and
36 in level 10. That is 61 cells in the whole game.
