# 09 — Leftovers, fossils and things nobody cleaned up

H.U.R.L. shipped with an unusual amount of its own making-of still attached.
Some of it is a naming change applied late and incompletely; some is a design
that was written, wired up and never used; and some is simply another
company's SDK sample data riding along on the retail disc.

## The game is called Slob Zone

The retail product is H.U.R.L. The thing on the disc is *Slob Zone 3D*, and
the rebrand stops at the outer layer.

| Where | What it says |
|---|---|
| `H.EXE` copyright block, `0x2ada0` | **H.U.R.L.** |
| `credits.gif`, `hurl.gif` | **H.U.R.L.** |
| the game's own C source file, in an assertion | **`slob.c`** |
| the out-of-memory message | **`Slob Zone needs at least 3Mb free.`** |
| title art in `GRAPH.RES` | `slobtitl.gif` and **three more** — see below |
| all ten between-level cards in `CUT.RES` | the **Slob Zone** logo, never the H.U.R.L. one |
| a name in `H.EXE` with no file behind it | **`slobad.gif`** |

The intro function at `0x12afe` runs straight through both brandings:
`slobad.gif` → `deeplogo.xmi` → `intro1.gif` → **`slobtitl.gif`** →
`mlogo.fli` → **`hurl.gif`** → `hurlcq.xmi` → `intro2.gif` → … →
`charscrn.gif`. Both title screens are shown, one after the other, and the
cutscene art was never redrawn.

`slobad.gif` — the "Slob ad" screen, and the very first thing the intro tries
to load — is one of only two file names in `H.EXE` that nothing on the disc
can satisfy. The other is `trig.dat` ([01](01-executables.md)).

## Four title screens that were never meant to ship together

`GRAPH.RES` holds six title pictures. `H.EXE` names two of them. The other
four are never referenced by any literal string or filename template:

| Member | What it shows |
|---|---|
| `slobtitl.gif` | **SLOB ZONE 3D**, the cast lined up — *used* |
| `hurl.gif` | **H.U.R.L.**, a completely different painting — *used* |
| `slobttl1.gif` | the Slob Zone painting captioned **SPECIAL EDITION**, and *"FROM BOB'S GAS STATION TO THE HAIRBALL TRAILER PARK!"* |
| `slobttl2.gif` | the same painting captioned **3 WORLD EDITION** |
| `slobttl3.gif` | the same painting captioned **1 WORLD EDITION** |
| `hurl1.gif` | the Slob Zone painting with the **H.U.R.L.** logo pasted over it |

A one-world edition, a three-world edition and a special edition — a tiered
shareware/retail line-up that was drawn and abandoned. What shipped is ten
levels under a fourth name, and all four alternative title screens travelled
to the pressing plant inside the archive.

## An objective system that was built and never used

Three keywords Deep River added to the level parser are used by no shipped
level: `LevelType:`, `Timer:` and `Rect:`. All three are fully implemented.

`Rect:` parses four integers with `sscanf(rest, "%d, %d, %d, %d", …)` into
four globals, and those globals are read at `0x14ef8` by a loop over the
engine's object list that converts each object's position to a cell and tests
whether it falls inside the rectangle. A level type, a countdown timer, and a
trigger rectangle tested for the presence of objects — written, wired up, and
never switched on. See [01-executables.md](01-executables.md).

The fourth unused keyword, `PALFILE:`, is ACK-3D's own, and is parsed as a
*number* rather than a file name.

## `PICS.DTF` is an old copy of level 2

681,498 bytes, 289 chunks, and it is not a picture archive. Chunk by chunk
against `LEV2.DTF` (681,484 bytes, 289 chunks): **287 of the 289 chunks are
byte-identical**. Only the level script and the map differ.

The script differences are a snapshot of level 2 being tuned:

```
PICS:  Destroy: ANIMATE|MULTIVIEW|MOVEABLE,1,6,116,116,117,117,118,118
LEV2:  Destroy: ANIMATE|PASSABLE|MOVEABLE,1,6,116,116,117,117,118,118      (x10)

PICS:  Destroy: ANIMATE|SHOWONCE,1,6,73,73,74,74,75,75
LEV2:  Destroy: ANIMATE|PASSABLE,1,6,73,73,74,74,75,75

PICS:  Number: 104,1,142,0      LEV2:  Number: 104,1,20,0
PICS:  Number: 105,1,142,1440   LEV2:  Number: 105,1,20,1440
PICS:  Number: 106,1,142,480    LEV2:  Number: 106,1,20,480
PICS:  Number: 142,1,147,0      LEV2:  Number: 142,1,19,0
```

Eleven objects had `MULTIVIEW`/`SHOWONCE` swapped for `PASSABLE` on their
destruction state, and four moved from the scenery type range (142, 147) into
the interactive range (20 = TOILET, 19 = HYDRANT WET). The map differs too:
`PICS` places 125 objects where `LEV2` places 130.

Whichever direction the edit went, `PICS.DTF` is a full second copy of a
level — 681 kB of the disc — that the game never loads under that name, since
it builds level file names from `lev%d.dtf`.

## The projectile pool, parked off the map

ACK-3D allocates nothing at run time: every object that can ever exist has to
be declared in the level script and placed in the map's object grid before the
level starts. Water balloons, bars of soap, cans of deodorant, duck eggs,
flies, kitty litter and banana spit are all objects, so every one that can be
in flight at once has to be somewhere on the map at load.

The designers put them in a corner. In `LEV1`:

```
  ( 0, 0) #78  DUCK EGG-1        type 5
  ( 1, 0) #80  DUCK EGG-2        type 5
  …
  ( 0, 3) #1   WATER BALLOON-1   type 5
  ( 0, 4) #6   BAR OF SOAP-1     type 6
  ( 0, 5) #11  DEODORANT-1       type 7
```

Five of each, stacked in rows in the sealed nine-by-eleven room in the
top-left of the map — and the first column of each row sits at `x = 0`, which
the map grid marks as solid border wall. In ten of the eleven level files
**every** projectile-class object (types 5, 6, 7 and 15) is in that top-left
block; the eleventh, `LEV4`, uses the same trick shifted to `x = 28…35` along
the top edge.

This is also why the level scripts contain 1,541 object definitions for about
thirty kinds of thing: `WATER BALLOON-1` through `-5` are five separate,
identical, fully written-out blocks because five water balloons exist.

## Nine of the eleven maps carry nothing but a copied template

Every map chunk ends with a list of per-cell records. Ten of them are shared
across level files — five appear in **all eleven**, five more in seven — and
in nine of the eleven files those copied records are the *only* records
present. In most levels the cells they name are empty in all three wall grids,
so they point at nothing.

Only `LEV1` (11 of its 21) and `LEV10` (8 of 18) contribute records of their
own. Somebody made a template level early on and every level since carried its
leftovers. [04-maps.md](04-maps.md) has the table.

> **Correction.** The first pass of this repository reported a "1040-byte
> uninitialised gap" in every map chunk, holding fossilised level-compiler
> memory in six of the ten levels. That was wrong: it came from assuming six
> equal 8192-byte planes. `AckReadMapFile` actually reads xGrid and yGrid as
> **8712** bytes each, and what looked like a gap is the tail of the ceiling
> grid — real data. The repeated values in levels 3, 4, 6, 7, 8 and 9 are
> those levels' ceilings, not stale memory.

## Somebody else's SDK demo, on the retail disc

Four files on the disc belong to the MIDPAK/DIGPAK sound SDK, not to the game,
and two of them are readable text:

**`SETD.DES`**
```
SETD.SND: Rob Wallace
    Origninal Music by: Rob Wallace, composed for Roland Sound Canvas
    and digitized into 8 bit sound by John W. Ratcliff for this
    demo.
```

**`SETM.DES`**
```
SETM.XMI: Rob Wallace
    Hit ENTER then PRESS '1' or '2' or '3' or '4' to hear the Techno-
    Pop Loops for SPACE.  As the user interacts with the program,
    specific music plays. Origninal Music by: Rob Wallace
```

`SETM.XMI` is the only XMIDI file on the disc that declares **five sub-songs**
instead of one — because it is the four-loop demo those instructions describe.
`SETD.SND` is its digitised counterpart, 47,616 bytes. Both are dutifully
copied to the player's hard disk by `INSTALL.DAT`. "SPACE" is some other,
unnamed project; the typo "Origninal" is in both files.

## And the `.NFO`

The copy examined also carries `DYNAMIX.NFO` — an ANSI-art release note from a
1995 warez group calling itself Dynamix (nothing to do with the Sierra
studio), reading `HURL FULL CD RIP (c) MILLENNIUM MEDIA CORP`, supplied
05/10/95, cracked `n/a`, nine disks, described as *"3D Cartoon Doom Style Game
with Wacky Animation good for all ages."*

It is not part of the game — it is the provenance of this particular
directory, and it is noted here so nobody mistakes it for one
([00-overview.md](00-overview.md)).

## Smaller things

* **The retail build is its own level test harness.** Alongside the
  documented `-s`, `H.EXE` accepts `-l<n>` to start on any level 1–10, `-f`
  to load an arbitrary level file by name, `-n` to skip the intro, `-g` for
  god mode and `-c` for a fourth mode. Switches may be introduced with `-`
  *or* `/`, and the letters are matched case-insensitively.

* **Every angle in the level scripts is wrong by the comment's own
  arithmetic.** The scripts document directions as 1920 units to the turn; the
  engine wraps at 1800. A "90°" in the data is 96° in the game.
  See [03-level-scripts.md](03-level-scripts.md).

* **`HURL4M.BAT`** on the disc is not what the installer writes. The installer
  generates `HURL4MEG.BAT` pointing at the CD; the file actually shipped
  points at a developer's machine:

  ```
  g:
  cd \release\millen
  set DOS4GVM=@NEW4G.VMC
  h -d c:\HURL\ %1 %2 %3 %4 %5 %6 %7
  ```

  `G:\RELEASE\MILLEN` — the build share, and the project's internal folder
  name, "millen" for Millennium.

* **Debug output survived into the retail build**: an FPS counter, a
  `pic%04d.raw` screen dump, per-hit tracing of objects, X-walls, Y-walls and
  doors, and `DANGER:` warnings on the engine's own object arrays.

* **`ERR_TOMANYVIEWS`** is spelled that way in the engine's error table, and
  `VECTOR.COM` describes itself as a `REAL-MODE INTERUPT VECTOR TRAPPER`.

* **`PIOGBOU.SND`** — the pig-bounce sound the engine loads by name has its
  `O` and `G` transposed, and it coexists with `PIGBOU2.SND`. Separately,
  `PIGBOUNC.SND` and `PIGHIT.SND` are byte-identical files.

* **`looser.gif`** is the losing screen.

* **`credits.gif` says © 1994**; the executable's copyright block says © 1995.

* **The back half of the game reruns the front half's audio**: `7.XMI` =
  `3.XMI`, `8.XMI` = `4.XMI`, `9.XMI` = `6.XMI` byte for byte, and `BOB9.RES`
  contains exactly the same sixteen speech clips as `BOB6.RES`, merely
  reordered. Ten levels, seven pieces of music, seven telephone calls.

* **Deluxe Paint's own bookkeeping** — a `GRAB` hotspot, a `TINY` thumbnail
  and sixteen `CRNG` colour-cycle ranges — is still inside the font image in
  `KIT.OVL` ([05-graphics.md](05-graphics.md)).

* **661 of the game's 684 distinct bitmaps can be recovered by their original
  artist file names**, because every wall and object entry in every level
  script carries the source `.gif` name in a trailing comment: `brick-1.gif`,
  `pigbnc1a.gif`, `dukwak3c.gif`, `twister7.gif`, `hedge.gif`, `mailbox.gif`.
