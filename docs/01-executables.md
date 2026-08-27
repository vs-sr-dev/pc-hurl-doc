# 01 — The executables and `KIT.OVL`

```sh
python tools/hurlexe.py "<install>" ident
python tools/hurlexe.py "<install>" keywords
python tools/hurlexe.py "<install>" trig
python tools/hurlexe.py "<install>" ghosts
python tools/hurlexe.py "<install>" strings H.EXE
```

## The six binaries

| File | Bytes | What it is |
|---|---:|---|
| `H.EXE` | 179,369 | the game. MZ stub + `LE` linear image at `0x2a88`, Watcom C, DOS/4GW |
| `DOS4GW.EXE` | 254,556 | Rational Systems DOS/4GW 32-bit extender, unmodified |
| `INSTALL.EXE` | 203,575 | Knowledge Dynamics *The Installer*, driven by `INSTALL.DAT` ([07](07-install-and-runtime.md)) |
| `SETD.EXE` | 76,160 | `DIGPAK Sound Driver Setup Program V3.3`, Borland C++ |
| `SETM.EXE` | 51,456 | the matching MIDPAK setup, Borland C++ |
| `SETSOUND.EXE` | 18,682 | a menu that runs the other two, Borland C++ |

`SETD.EXE` carries the string `Deep River Publishing` — the SDK's setup
program was rebuilt with the publisher's name in it. Otherwise all three
sound-setup programs are stock John W. Ratcliff / John Miles code, down to the
credits panel thanking Turtle Beach and Miles Design.

## What `H.EXE` says about itself

The interesting strings all sit in one run of the data segment, roughly
`0x2a200`–`0x2b400`. In address order:

### The ACK-3D error table (`0x2a204`)

```
ERR_BADFILE      ERR_BADCOMMAND    ERR_BADOBJNUMBER  ERR_BADSYNTAX
ERR_LOADINGBITMAP ERR_BADDIRECTION ERR_BADSTARTX     ERR_BADSTARTY
ERR_BADANGLE     ERR_BADMAPFILE    ERR_READINGMAP    ERR_BADPICNAME
ERR_INVALIDFORM  ERR_NOPBM         ERR_BADPICFILE    ERR_NOMEMORY
ERR_BADPALFILE   ERR_BADWINDOWSIZE ERR_TOMANYVIEWS   ERR_BADOBJECTNUM
ERR_BADOBJTYPE
```

Twenty-one names, stored as printable text — the engine reports parse failures
by symbol name. `ERR_TOMANYVIEWS` is misspelled in the shipped binary.

### The level-script keyword table (`0x2a3a7`–`0x2a5a0`)

Every keyword the `.INF` parser understands. The addresses matter: ACK-3D's
own keywords occupy `0x2a3a8`–`0x2a4cc` and then resume at `0x2a554`, and
Deep River's eleven additions sit in one contiguous block at
`0x2a4d8`–`0x2a53c` — **inserted into the middle of the engine's own table**.

| Origin | Keywords |
|---|---|
| ACK-3D (stored upper case) | `NUMBER: CREATE: DESTROY: WALK: ATTACK: INTERACT: END: LOADTYPE: BITMAPS: ENDBITMAPS: ENDDESC: ENDWALLS: OBJDESC: ENDOBJECTS: WALLS: OBJECTS: MAPFILE: PALFILE: XPLAYER: YPLAYER: PLAYERANGLE: SCREENBACK: SCROLLBACK: TOPCOLOR: BOTTOMCOLOR: SHADING: FLOORS: RESOLUTION:` and the flags `ANIMATE MOVEABLE PASSABLE MULTIVIEW SHOWONCE` |
| Deep River (stored mixed case) | `RedDoor: GreenDoor: BlueDoor: Vend: Hitgrid: Exit: Phone: Shower: LevelType: Timer: Rect:` |

The capitalisation split is not cosmetic. The shipped `.INF` files write
`MapFile:`, `xPlayer:`, `Walls:` in mixed case yet the strings in the binary
are `MAPFILE:`, `XPLAYER:`, `WALLS:` — so the engine upper-cases the token
before comparing. The eleven Deep River keywords are stored with exactly the
capitalisation the `.INF` files use, which is the signature of a literal
comparison added alongside the original parser rather than inside it.

Four keywords are never used by any shipped level: **`PALFILE:`** (ACK-3D's,
for an external palette) and **`LevelType:`, `Timer:`, `Rect:`** (Deep
River's). `Rect:` is immediately followed in the data segment by the format
string `%d, %d, %d, %d`, so it took four integers. See
[10-open-questions.md](10-open-questions.md).

### Debug output that survived into the retail build

```
FPS: %6ld, %d
Object %d hit at location %d
Xwall %d hit  at location %d
Ywall %d hit  at location %d
Door %d hit   at location %d
Loading file <%s>
Loading file level %d, <%s>
LoadNewLevel: error reading file <%s>
Allocating memory...
Total mem allocated = %ld
Sound System found / Sound System NOT found.
Mouse found. / No mouse found.
DANGER:  MoveObjectList[%d] is 255
DANGER:  ObjectsSeen[%d] is 255
No Intro
God Mode!
pic%04d.raw
```

`God Mode!` and `No Intro` are the two messages a developer switch prints.
`pic%04d.raw` is a numbered screen-dump filename. How any of the three is
triggered is not resolved here — the switches are compared as characters in
code, and no option string survives in the data segment.

The `Xwall` / `Ywall` pair is worth noting on its own: it confirms that the
engine keeps its walls in two separate grids, which is exactly what the map
chunk contains ([04-maps.md](04-maps.md)).

### Assertions, with the engine's source file names

```
Assertion failed: %hs, file %hs, line %d
ACKLDBMP.C   oNum >=0 / oNum < 255 / MoveObjectCount < 254
ACKPOV.C     MoveObjectCount >=0 && MoveObjectCount < 255
ACKVIEW.C    oCount>=0 / oCount<255 / i>=0 && i<255
slob.c       fName != NULL / buf != NULL
```

Three ACK-3D translation units and one of the game's own, `slob.c`.

### Two ghost names

`tools/hurlexe.py ghosts` resolves 83 of the 85 literal file names in `H.EXE`
against the disc. The two that resolve against nothing:

* **`trig.dat`** — ACK-3D loads its trigonometry tables from a file of this
  name. There is no `TRIG.DAT` on the disc; the tables are the first chunk of
  `KIT.OVL` instead. The string is a leftover of the stock loader.
* **`slobad.gif`** — the "Slob ad" screen, referenced in the intro sequence
  between `intro.xmi` and `deeplogo.xmi`, and present in no archive.
  (The tool prints it as `bslobad.gif`: Watcom pooled the string table with no
  padding, so a match picks up the last byte of its neighbour.)

Six further names are built at run time — `lev%d.dtf`, `%d.xmi`,
`phone%d.gif`, `qcut%d.gif`, `qcut%d.snd`, `pic%04d.raw` — plus `bob%d`,
which selects the per-level speech archive. (The tool prints these with the
same pooling junk on the front: `eylev%d.dtf`, `ey%d.xmi`, `gphone%d.gif`.)

## `KIT.OVL` — the engine's lookup tables and its font

`KIT.OVL` uses the same container format as the `.DTF` level files
([02](02-containers.md)) and holds exactly three chunks. `H.EXE` opens it by
name and fails with `Unable to open resource KIT.OVL`.

### Chunk 0 — 50,400 bytes: seven trigonometry tables

12,600 `int32`, i.e. **7 tables of 1800 entries**. 1800 steps per turn means
one unit is 0.2°. Verified against the real functions:

| Table | Contents | `[0]` | `[225]` (45°) | `[450]` (90°) |
|---:|---|---:|---:|---:|
| 0 | sin × 65536 | 0 | 46341 | 65536 |
| 1 | cos × 65536 | 65536 | 46341 | 1 |
| 2 | tan × 65536 | 0 | 65536 | `INT32_MAX` |
| 3 | cot × 65536 | `INT32_MAX` | 65537 | 3 |
| 4 | (1/cos) × 1048576 | 1048576 | 1482911 | `INT32_MAX` |
| 5 | (1/sin) × 1048576 | `INT32_MAX` | 1482911 | 1048576 |
| 6 | cos × 16384 | 16384 | 11586 | 1 |

Poles are clamped to `INT32_MAX` rather than left undefined. This is the file
`H.EXE` still calls `trig.dat`.

Note the mismatch with the level scripts: every `.INF` file comments its
direction field as `30=160, 45=240, 90=480, 180=960, 270=1440`, i.e. 1920
units to the turn, while these tables are 1800. See
[10-open-questions.md](10-open-questions.md).

### Chunk 1 — 8,192 bytes: a second cosine table

4,096 `int16` = **cos × 16384 over 4096 steps per turn**, worst deviation from
the true cosine 1 part in 16384. A different angular resolution from the
tables above, so it belongs to game code rather than to the caster.

### Chunk 2 — 2,332 bytes: the font

An IFF `PBM ` image, **294 × 5**, ByteRun1-compressed, 8 bitplanes,
`masking = 2` with transparent index 5. It is an ASCII strip in code-point
order beginning at space and ending at `Z` — 59 glyphs at a five-pixel pitch,
upper case only, which is why every string the game draws is upper case. The
error message when it will not load is `Error loading font BBM.`

The chunk also keeps three chunks Deluxe Paint wrote and nobody stripped: a
`GRAB` hotspot at (147, 2), a `TINY` thumbnail, and sixteen `CRNG`
colour-cycle ranges ([05-graphics.md](05-graphics.md)).
