# 03 — The level scripts

Chunk 0 of every `.DTF` is not data. It is a **plain-ASCII, heavily commented
configuration file**, shipped verbatim on the retail disc, complete with the
designers' own explanations of every field and the source `.gif` name of every
bitmap in a trailing comment. `LEV1` opens:

```
; Info file for each level
; This is the index to the map file to use
MapFile: 1

; Initial coordinates of POV
xPlayer: 1835
yPlayer: 2271

; Initial angle of POV, if left out then a random angle will be given
PlayerAngle: 1448
```

Sizes run from 39,771 bytes (`LEV1`) to 74,429 (`LEV9`); across the eleven
files there are 1,541 object definitions and **661 distinct source file names
recoverable from the comments**, against 684 distinct images actually shipped.

```sh
python tools/hurlinf.py "<install>" text LEV1     # the script, verbatim
python tools/hurlinf.py "<install>" header        # all eleven headers
python tools/hurlinf.py "<install>" objects LEV1
python tools/hurlinf.py "<install>" types         # the type-ID census
python tools/hurlinf.py "<install>" assets        # recovered .gif names
```

## Grammar

Line-oriented. `;` starts a comment and runs to end of line; blank lines are
ignored. Every statement is `Keyword: values`, except inside a `Bitmaps:`
block, where a line is a bare `slot,resource` pair. `End:` is mandatory — the
comment in the file says so.

```
Walls:                  Objects:                ObjDesc:
  Bitmaps:                Bitmaps:                Number:  n,speed,type,dir
    wall,resource           slot,resource         Create:  flags,views,per,…
    …                       …                     Destroy: …
  EndBitmaps:             EndBitmaps:             Walk:    …
EndWalls:               EndObjects:               Attack:  …
                                                  Interact: …
                                                EndDesc:
                                                End:
```

`Objects:`…`EndObjects:` encloses both the object bitmap table and the
`ObjDesc:` block; `EndBitMaps:` appears with that exact capitalisation in two
files, which the parser accepts because it upper-cases the token first.

## Header fields

Every keyword is documented in [01-executables.md](01-executables.md), which
also shows which came from ACK-3D and which Deep River added. The eleven
shipped headers:

| Level | xPlayer | yPlayer | Angle | Top | Bottom | Shade | Floors | Res | Back | Sky | Phone | Hitgrid |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| LEV1 | 1835 | 2271 | 1448 | 174 | 12 | OFF | ON | 2 | 2 | 3 | 9 | – |
| LEV2 | 260 | 2140 | 0 | 174 | 108 | OFF | ON | 2 | 2 | 3 | 100 | – |
| LEV3 | 2140 | 2592 | 1440 | 0 | 90 | OFF | ON | 2 | 2 | 3 | 9 | 18 |
| LEV4 | 2015 | 3265 | 1440 | 174 | 12 | OFF | ON | 2 | 2 | 3 | 9 | – |
| LEV5 | 2000 | 2299 | 247 | 174 | 108 | OFF | ON | 2 | 2 | 3 | 9 | – |
| LEV6 | 2105 | 2296 | 1482 | 174 | 12 | OFF | ON | 2 | 2 | 3 | 9 | 48 |
| LEV7 | 2057 | 2135 | 337 | 0 | 90 | OFF | ON | 2 | 2 | 3 | 49 | 18 |
| LEV8 | 1300 | 1125 | 480 | 174 | 12 | OFF | ON | 2 | 2 | 3 | 9 | 12 |
| LEV9 | 2220 | 880 | 452 | 174 | 108 | OFF | ON | 2 | 2 | 3 | 58 | 48 |
| LEV10 | 2150 | 2465 | 1440 | 174 | 200 | OFF | ON | 2 | 2 | 3 | 52 | – |
| PICS | 260 | 2140 | 0 | 174 | 108 | OFF | ON | 2 | 2 | 3 | 100 | – |

Constant across the whole game: `MapFile: 1`, `ScreenBack: 2`,
`ScrollBack: 3`, `LoadType: 1`, `Shading: OFF`, `Floors: ON`,
`Resolution: 2`. Shading is off in every single level — the engine supports
distance shading and the game never turns it on.

Player coordinates are in world units at **64 units per map cell**: dividing
each start position by 64 lands on an empty cell of the wall grid in ten of
the eleven files (the exception is `LEV8`, which starts on wall value 39).

`Hitgrid:` is the "step here and take damage" wall index, and appears in only
five levels: 3, 6, 7, 8 and 9.

`RedDoor:`/`GreenDoor:`/`BlueDoor:`/`Vend:`/`Exit:`/`Shower:`/`Phone:` all name
a **wall slot**, not an object — doors, vending machines, exit signs, showers
and telephones are walls the engine treats specially. `LEV2`/`PICS` use a
completely different slot range (96–102) from every other level, because their
wall table is twice as long.

## The wall table

```
Walls:
  Bitmaps:
  ; Wall Number, Resource Number
  LoadType: 1
  1,46    ;shower.gif
  2,47    ;shower2.gif
  …
  13,54   ; brick-1.gif   begin level specific walls
```

Left number is the wall slot referenced from the map grid; right number is a
**chunk index inside this same `.DTF`**. Slots 1–12 are the fixed furniture
(shower, curtain, three locked doors, vending machine, wall phone, phone
booth, two exit signs) and the comment `begin level specific walls` marks
where the level's own art starts. Levels declare between 52 and 103 walls.

## The object table and object descriptions

```
Objects:
  Bitmaps:
  ; Bitmap number, Resource Number
  1,4     ;balloon1.gif
  …
  39,94   ;pigbnc1a.gif         start of objects, max up to #311
  EndBitmaps:
  ObjDesc:
  ;PIG-1
  ;Number,Speed,ID#,Direction(30=160,45=240,90=480,180=960,270=1440)
  Number: 71,15,1,480
  ; Flags,Number of Views,Bitmaps per view,Bitmaps
  Create:   ANIMATE|MULTIVIEW|MOVEABLE,8,4,55,55,56,56,…
  Destroy:  ANIMATE,8,4,55,55,…
  Walk:     ANIMATE|MULTIVIEW|MOVEABLE,8,4,39,39,40,40,…
  Attack:   ANIMATE|MULTIVIEW|MOVEABLE|SHOWONCE,8,4,39,39,…
  Interact: ANIMATE|SHOWONCE,8,4,39,39,…
```

`Number:` takes four values — **instance number, speed, type ID, facing**.
The instance number is what the map's object plane stores, so *every placed
object gets its own full definition*: `LEV1` contains five identical
`WATER BALLOON-1` … `-5` blocks because five water balloons appear on the map.
Across the game that produces 1,541 definitions for what is really about
thirty kinds of thing.

`Speed` is 1 for 893 of the 1,541 definitions (static scenery); moving things
use 9–61, and the projectile speed is uniformly 61.

`Direction` uses **1920 units to the full turn**, exactly as the comment says:
the values that occur are 0 (1332×), 1440 = 270° (105×), 960 = 180° (53×),
1680 = 315° (33×), 480 = 90° (13×), and a handful of odd ones.

### States

Five states, each with the same shape: `flags, views, bitmaps-per-view,
bitmap list`. `Create`, `Destroy`, `Walk` and `Attack` appear on all 1,541
objects; `Interact` on 243 — only the eight named characters have it.

`views × bitmaps-per-view` is the length of the bitmap list. The distribution
is very regular:

| views × per-view | Count | Meaning |
|---|---:|---|
| 1 × 1 | 3,937 | a single still frame |
| 1 × 4 | 736 | a 4-step loop seen from any angle |
| **8 × 4** | 666 | **8 rotation views, 4 frames each — the walking enemies** |
| 1 × 6 | 481 | a 6-step loop (the standard destruction burst) |
| 1 × 8 | 267 | an 8-step loop |

Frames are usually listed twice in a row (`21,21,22,22`) — the engine advances
one entry per tick, so doubling an entry halves the animation rate. That is
the only speed control the format has.

### Flags

Five, `|`-separated, or a literal `0` for none.

| Flag | Uses | Effect |
|---|---:|---|
| `PASSABLE` | 2,203 | the player walks through it |
| `ANIMATE` | ~2,900 | step through the bitmap list |
| `MOVEABLE` | ~2,450 | the object has a position that changes |
| `MULTIVIEW` | ~1,900 | pick the bitmap set from the viewing angle |
| `SHOWONCE` | 768 | play the list once and stop |

The most common combinations are `PASSABLE` alone (pickups and litter),
`ANIMATE|MULTIVIEW|MOVEABLE` (a walking animal) and bare `0` (solid scenery).

## Type IDs

The third value of `Number:` is a type ID, and it is the game's real object
taxonomy. Counting every definition in every level and grouping by the
designers' own comment labels:

| ID | Count | Labels seen |
|---:|---:|---|
| 1 | 70 | PIG — *Ricochet Pig* |
| 2 | 51 | DUCK — *Quack Attacker* |
| 3 | 33 | CAT — *Sour Puss* |
| 4 | 22 | TRASH TWISTER |
| 5 | 249 | WATER BALLOON, FLY, KITTY LITTER, DUCK EGG, BANANA SPIT, SMOKE RING |
| 6 | 45 | BAR OF SOAP |
| 7 | 45 | DEODORANT |
| 8 | 22 | RAINCOAT |
| 9 | 22 | UMBRELLA |
| 10 | 22 | MOIST TOWELETTE |
| 11 / 12 / 13 | 11 each | RED / BLUE / GREEN key |
| 14 | 20 | GATOR — *Swamp Breath* |
| 15 | 10 | SOAP-X |
| 16 | **1** | BOB THE SLOB |
| 17 | 24 | MONKEY — *Baboon Spittoon* |
| 18 | 40 | FROG — *Bug Eye Frog* |
| 19 | 6 | HYDRANT WET |
| 20 | 11 | TOILET |
| 129 | 180 | EMPTY CAN 1/2/3 |
| 130 | 180 | BANANA, NEWPAPER, BONE |
| 131 | 239 | APPLE CORE, CEREAL BOX, TRASHCAN, shop signs |
| 132, 134, 135 | 34, 30, 55 | trashcans, statues, trees, shrubs, cactus, haystack, scarecrow |
| 137, 138 | 4, 4 | PHONE BOOTH, PHONE ON TABLE |
| 140–149 | 4–36 | shower, bath sink, toilet, fridge, easy chair, mailbox, dripping slime, lava lamp, table with vase, floor lamp |

Two things fall straight out of that table.

**The type space is split at 128.** IDs 1–20 are things that act — enemies,
ammunition, pickups, keys, projectiles. IDs 129 and up are scenery and litter.
IDs 21–128 are entirely unused, as are 133, 136, 139 and 143.

**Type 5 is "projectile", not "water balloon".** Everything thrown by anybody
shares it: the player's water balloon, the frog's fly, the cat's kitty litter,
the duck's egg, the monkey's banana spit and the gator's smoke ring.

**Type 16 appears exactly once in the whole game** — a single BOB THE SLOB.

The eight names on `charscrn.gif` — Ricochet Pig, Trash Twister, Quack
Attacker, Sour Puss, Bug Eye Frog, Swamp Breath, Baboon Spittoon, Bob the Slob
— map one-for-one onto types 1, 4, 2, 3, 18, 14, 17 and 16.

The three litter types match the three cash tiers on the instruction screen
exactly: `trshscrn.gif` prices the crushed can and the two bottles at 5¢
(type 129), the banana peel, bone and newspaper at 10¢ (type 130), and the
apple core and cereal box at 25¢ (type 131). Type 131 also covers trashcans
and shop signs, so the type alone cannot be the price — but the eight priced
bitmaps land in the right three buckets with nothing out of place.
