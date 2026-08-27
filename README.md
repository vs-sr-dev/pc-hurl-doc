# pc-hurl-doc

Reverse-engineering notes on **H.U.R.L.** (Deep River Publishing for
Millennium Media Group, 1995) — the MS-DOS shooter in which a boy throws water
balloons at cartoon animals and picks litter up off the floor for pocket
money, built on **Lary Myers' ACK-3D engine** and shipped with most of its own
making-of still attached.

This repository documents the **retail DOS release, version 1.0**: the eleven
`.DTF` level containers, the fourteen `.RES`/`.TAB` archives and the six
executables that install alongside them.

**Documentation only.** No game assets, no extracted art and no executable
code is committed here. The tools in [`tools/`](tools/) reproduce every table
and figure from your own legally obtained copy.

## What is documented

| Doc | Contents |
|---|---|
| [00-overview.md](docs/00-overview.md) | Release, credits, build chain, file inventory, provenance |
| [01-executables.md](docs/01-executables.md) | `H.EXE` and the five helpers; reading the LE image; the ACK-3D fingerprints; the parser keyword table; the seven command-line switches; `KIT.OVL`'s trig tables and font |
| [02-containers.md](docs/02-containers.md) | `.DTF` indexed chunks and `.RES`/`.TAB` named archives |
| [03-level-scripts.md](docs/03-level-scripts.md) | The commented ASCII level language, the object model, the type IDs |
| [04-maps.md](docs/04-maps.md) | The six grids as the loader reads them, the wall flag bits, the trailing record list |
| [05-graphics.md](docs/05-graphics.md) | GIF87a tiles, IFF-PBM backdrops, one palette for the whole game, the FLIC |
| [06-audio.md](docs/06-audio.md) | DIGPAK/MIDPAK, 19 Miles drivers, headerless `.SND`, XMIDI, The Fat Man's patch bank |
| [07-install-and-runtime.md](docs/07-install-and-runtime.md) | `INSTALL.DAT`, the generated batch files, the command line, the controls |
| [08-vs-ack3d.md](docs/08-vs-ack3d.md) | The ACK-3D lineage, what came from the engine, what Deep River added, what neither uses |
| [09-easter-eggs-and-leftovers.md](docs/09-easter-eggs-and-leftovers.md) | Slob Zone, four unused title screens, the unused objective system, the stale level copy, the projectile pool, the SDK demo on the retail disc |
| [10-open-questions.md](docs/10-open-questions.md) | What the disassembly settled, what it corrected, and what is still open |
| [notes/level-inventory.md](notes/level-inventory.md) | All eleven containers, per-plane cell counts, shared assets |
| [notes/object-catalogue.md](notes/object-catalogue.md) | The full type table, the cast, the trash economy |
| [notes/phone-calls.md](notes/phone-calls.md) | The ten speech banks and what they reuse |

## Highlights

**It is an ACK-3D game, and the credits say so out loud.** `credits.gif`
lists "3D GRAPHICS …… LARY MYERS" — the author of ACK-3D, the tile-based
ray-caster published with source in *The Amazing 3-D Games Adventure Set*, and
the first rung of the ladder that runs through ACKNEX to Conitec's 3D
GameStudio. `H.EXE` still carries the engine's assertion strings naming
`ACKVIEW.C`, `ACKPOV.C` and `ACKLDBMP.C`, its 21-entry `ERR_*` table, and the
two `$`-terminated panic messages `Screw up in XRAY$` and `Screw up in YRAY$`
from the assembly caster.

**The map format is documented from the loader, not guessed.**
`tools/hurlle.py` rebuilds the DOS/4GW linear image and applies its 4,275
fixup records, which makes cross-referencing exact. `AckReadMapFile` at
`0x1c270` turns out to read six grids of **8192, 8192, 8712, 8712, 8192,
8192** bytes — xGrid and yGrid are 4,356 entries (66 × 66, a guard border), not
4,096 — followed by a `uint16` count and that many 5-byte records. Every wall
flag then falls out of the code: `0x10` door, `0x40` locked, `0x20` sliding
wall, `0x08` see-through (the drawer writes 0 into the grid so the ray carries
on), `0x02`/`0x04` multi-height.

**The retail executable is its own test harness.** Seven command-line
switches, introduced with `-` *or* `/` and matched case-insensitively:
`-d` data path, `-s` no sound, `-n` skip the intro, **`-g` god mode**,
**`-l<n>` start on any level**, **`-f <file>` load an arbitrary level file**,
and `-c`. God mode is checked in exactly two places, both immediately before
the damage call.

**The levels ship as commented source.** Chunk 0 of every `.DTF` is a
plain-ASCII configuration file with the designers' own explanations in it —
`; Initial angle of POV, if left out then a random angle will be given` — and
every wall and object entry carries its source artwork file name in a trailing
comment. **661 of the game's 684 distinct bitmaps can be recovered by their
original artist file names** that way: `brick-1.gif`, `pigbnc1a.gif`,
`dukwak3c.gif`, `twister7.gif`.

**You can tell the engine's keywords from the game's by their
capitalisation.** The `.INF` files write `MapFile:` and `xPlayer:` in mixed
case, but the strings in `H.EXE` are `MAPFILE:` and `XPLAYER:` — ACK-3D
upper-cases the token before comparing. The eleven keywords stored *with* the
`.INF` capitalisation — `RedDoor:`, `Vend:`, `Hitgrid:`, `Phone:`, `Shower:`,
`LevelType:`, `Timer:`, `Rect:` … — are Deep River's additions, and they sit
in one contiguous block wedged into the middle of the engine's own string
table. Four keywords are parsed and never used by any shipped level.

**The game is really called Slob Zone.** The retail brand stops at the title
screen. The game's own source file is `slob.c`, the out-of-memory message is
`Slob Zone needs at least 3Mb free.`, the intro shows *both* title screens one
after the other, and all ten between-level cutscene cards carry the **Slob
Zone 3D** logo and never the H.U.R.L. one.

**Three editions that never happened are still in the archive.** Besides the
two title screens the game uses, `GRAPH.RES` carries four more that nothing
references: the Slob Zone painting captioned **SPECIAL EDITION** ("FROM BOB'S
GAS STATION TO THE HAIRBALL TRAILER PARK!"), **3 WORLD EDITION**, **1 WORLD
EDITION**, and the same painting with the H.U.R.L. logo pasted over it.

**An objective system was built and switched off.** `LevelType:`, `Timer:`
and `Rect:` are parsed by the level loader and used by no level. `Rect:`
`sscanf`s four integers into globals that a working bounding-box test reads
back, walking the object list to see what is inside the box.

**Every angle in the level scripts is wrong.** The scripts document object
facings as 1920 units to the turn — `90=480, 180=960, 270=1440` — and the
engine wraps at **1800**. What the designers wrote as 90° the game renders as
96°.

**Every projectile in the game is parked off the edge of the map.** ACK-3D
allocates nothing at run time, so each water balloon, bar of soap, can of
deodorant and duck egg has to exist as a placed map object before the level
starts. In ten of the eleven level files, *every* projectile-class object sits
in a sealed room in the top-left corner of the grid — five of each, in rows,
some of them inside the border wall. It is also why the scripts contain 1,541
object definitions for about thirty kinds of thing: `WATER BALLOON-1` through
`-5` are five separate fully written-out blocks.

**`PICS.DTF` is a stale copy of level 2.** 287 of its 289 chunks are
byte-identical to `LEV2.DTF`; only the script and the map differ, and the
differences are a snapshot of the level being tuned — eleven objects with
`MULTIVIEW` swapped for `PASSABLE`, four moved from the scenery type range
into the interactive one, five fewer objects placed. 681 kB of disc for a
level the game never loads under that name.

**Nine of the eleven maps carry nothing but a copied template.** Every map
chunk ends with a list of per-cell records. Ten of them recur across files —
five in all eleven — and in nine of the eleven those copies are the *only*
records present, mostly pointing at cells that are empty in all three wall
grids. Only levels 1 and 10 add any of their own.

**Somebody else's SDK demo shipped on the retail disc**, with its
instructions: `SETM.DES` explains how to "PRESS '1' or '2' or '3' or '4' to
hear the Techno-Pop Loops for SPACE", and `SETM.XMI` is the only XMIDI file on
the disc with five sub-songs, because it is that demo. The installer copies
both to the player's hard drive.

**The back half of the game reruns the front half.** `7.XMI` = `3.XMI`,
`8.XMI` = `4.XMI`, `9.XMI` = `6.XMI` byte for byte, and `BOB9.RES` holds
exactly the same sixteen speech clips as `BOB6.RES`, reordered. Ten levels,
seven pieces of music, seven telephone calls.

## Tools

Pure Python 3. `pillow` is needed for the image paths and `numpy` for the map
run-length report; everything else is standard library.

```
tools/hurllib.py     Containers, .TAB directories, GIF/PBM decoding, map and .INF parsing
tools/hurldtf.py     .DTF / .OVL chunk listing, extraction and census
tools/hurlres.py     .RES / .TAB archive listing and extraction
tools/hurlinf.py     Level scripts: headers, object tables, type census, recovered asset names
tools/hurlmap.py     Map grids: ASCII, PNG, wall flag bits, object cross-reference, plane evidence
tools/hurlgfx.py     GIF tiles, IFF-PBM backdrops, palettes, the font, the FLIC
tools/hurlaudio.py   .SND to WAV, speech banks, XMIDI inventory, FAT.OPL, driver identification
tools/hurlexe.py     Executable identification, keyword table, trig tables, ghost file names
tools/hurlle.py      Loads the DOS/4GW LE image, applies its fixups, cross-references, disassembles
tools/hurlexport.py  One shot: everything above into one directory
```

```sh
python tools/hurlexport.py "<install>" ./out
```

or piecemeal:

```sh
python tools/hurldtf.py   "<install>" census
python tools/hurlinf.py   "<install>" types
python tools/hurlmap.py   "<install>" walls
python tools/hurlmap.py   "<install>" objects LEV1
python tools/hurlgfx.py   "<install>" palettes
python tools/hurlaudio.py "<install>" xmi
python tools/hurlexe.py   "<install>" keywords
python tools/hurlle.py    "<install>" info
```

`hurlle.py` needs `capstone` for its `dis` and `func` subcommands; `info`,
`xref` and `strings` are standard library only.

`<install>` is the directory holding `H.EXE` and the `*.DTF` files.

## Status

Second pass. The first pass documented the formats from the data; this one
reads them out of the executable, which settled nine of the ten questions the
first pass left open — and corrected one of its answers. Chapter 10 lists what
is closed, what is still open, and the one conclusion that had to be
withdrawn: there is no 1,040-byte gap in the map chunk, and the "fossilised
level-compiler memory" it seemed to contain is just the tail of the ceiling
grid.

What remains open is chiefly the `-c` switch, what the per-cell record lists
draw, and the difference between wall flags `0x02` and `0x04`.
