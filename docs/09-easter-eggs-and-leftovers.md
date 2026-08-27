# 09 — Leftovers, fossils and things nobody cleaned up

H.U.R.L. shipped with an unusual amount of its own making-of still attached.
Some of it is a naming change that was applied late and incompletely; some is
a build pipeline that wrote out buffers it had not filled; and some is simply
another company's SDK sample data riding along on the retail disc.

## The game is called Slob Zone

The retail product is H.U.R.L. The thing on the disc is *Slob Zone 3D*, and
the rebrand stops at the outer layer.

| Where | What it says |
|---|---|
| `H.EXE` copyright block, `0x2ada0` | **H.U.R.L.** |
| `credits.gif`, `hurl.gif`, `hurl1.gif` | **H.U.R.L.** |
| the game's own C source file, in an assertion | **`slob.c`** |
| the out-of-memory message | **`Slob Zone needs at least 3Mb free.`** |
| title art in `GRAPH.RES` | `slobtitl.gif`, `slobttl1/2/3.gif` — a full **SLOB ZONE 3D** title screen with the cast lined up |
| all ten between-level cards in `CUT.RES` | the **Slob Zone** logo, never the H.U.R.L. one |
| a name in `H.EXE` with no file behind it | **`slobad.gif`** |

Both title screens are present and both are referenced by the executable, in
the same intro run (`intro.xmi`, `slobad.gif`, `deeplogo.xmi`, `intro1.gif`,
`slobtitl.gif`, `mlogo.xmi`, `mlogo.fli`, `hurl.gif`, `hurlcq.xmi` …), so the
disc can show you either one. The cutscene art was never redrawn.

`slobad.gif` — the "Slob ad" screen — is one of only two file names in
`H.EXE` that nothing on the disc can satisfy. The other is `trig.dat`, the
name ACK-3D uses for the trig tables that here live inside `KIT.OVL`
([01-executables.md](01-executables.md)).

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
destruction state, and four objects were moved from the scenery type range
(142, 147) into the interactive range (20 = TOILET, 19 = HYDRANT WET). The map
also differs: `PICS` places 125 objects where `LEV2` places 130.

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
  ( 1, 3) #2   WATER BALLOON-2   type 5
  …
  ( 0, 4) #6   BAR OF SOAP-1     type 6
  ( 0, 5) #11  DEODORANT-1       type 7
```

Five of each, stacked in rows in the sealed nine-by-eleven room in the
top-left of the map — and the first column of each row sits at `x = 0`, which
plane 0 marks as solid border wall. In ten of the eleven level files **every
single projectile-class object** (types 5, 6, 7 and 15) is in that top-left
block; the eleventh, `LEV4`, uses the same trick shifted to `x = 28…35` along
the top edge.

This is also why the level scripts contain 1,541 object definitions for about
thirty kinds of thing: `WATER BALLOON-1` through `-5` are five separate,
identical, fully written-out blocks because five water balloons exist.

## The map compiler's uninitialised buffer

Every map chunk has 1040 unused bytes between the grids and the trailing
record list. In five files they are zero. In the other six they hold one tile
index repeated hundreds of times — `19` in LEV3 and LEV7, `29` in LEV4 and
LEV8, `16` in LEV6, `13` in LEV9 — which is what the tail of a floor-plane
fill looks like. Six of the ten shipped levels carry a fossil of the level
compiler's own working memory ([04-maps.md](04-maps.md)).

## Five records copied into every level

The trailing record list of the map chunk starts, in **all eleven files**,
with the same five records:

```
cell  449 (1, 7)   value 0    extra 0
cell  647 (7,10)   value 5    extra 0
cell  661 (21,10)  value 6    extra 3
cell  771 (3,12)   value 2    extra 1541
cell 2278 (38,35)  value 16   extra 9265
```

Five more are shared by seven of the eleven. The `extra` field is zero in
every genuine, level-specific record — and the only two records with garbage
in it, 1541 and 9265, are among the five that never change. Somebody made a
template level, and every level since has carried its leftovers.

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

* **Debug output survived into the retail build**: an FPS counter, a
  `pic%04d.raw` screen dump, per-hit tracing of objects, X-walls, Y-walls and
  doors, and the two developer switches that print `God Mode!` and `No Intro`.

* **Deluxe Paint's own bookkeeping** — a `GRAB` hotspot, a `TINY` thumbnail
  and sixteen `CRNG` colour-cycle ranges — is still inside the font image in
  `KIT.OVL` ([05-graphics.md](05-graphics.md)).

* **661 of the game's 684 distinct bitmaps can be recovered by their original
  artist file names**, because every wall and object entry in every level
  script carries the source `.gif` name in a trailing comment: `brick-1.gif`,
  `pigbnc1a.gif`, `dukwak3c.gif`, `twister7.gif`, `hedge.gif`, `mailbox.gif`.
