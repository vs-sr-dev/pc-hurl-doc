# 08 — What is ACK-3D and what is Deep River

H.U.R.L. is an **ACK-3D** game. ACK-3D is Lary Myers' tile-based ray-caster,
published with source in *The Amazing 3-D Games Adventure Set* (Coriolis
Group, 1995) and licensed for commercial use. Myers is credited on the game's
own credits screen as "3D Graphics".

This chapter separates the engine from the game, using only what is in the
shipped files.

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

**The map model**: a 64 × 64 grid, separate X and Y wall grids, an object
grid, floor and ceiling grids, doors keyed by colour.

**The trig tables**: seven tables of 1800 `int32` at 0.2° per step, poles
clamped to `INT32_MAX` ([01-executables.md](01-executables.md)).

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
| `Hitgrid:` | a wall you take damage from standing on | 5 levels |
| `LevelType:` | — | **never** |
| `Timer:` | — | **never** |
| `Rect:` | four integers (`%d, %d, %d, %d` follows it in the data segment) | **never** |

Every one of these is a *wall*, not an object — the game's interactive
furniture is implemented as special wall indices the engine is told about up
front, which is how you add doors, phones and showers to a caster that has no
concept of any of them.

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
* `LevelType:`, `Timer:` and `Rect:` are parsed and never written.
* The `XRAYMULTI`/`YRAYMULTI` panic strings imply the multi-height casting
  path is linked in; nothing in the shipped maps obviously uses it.
