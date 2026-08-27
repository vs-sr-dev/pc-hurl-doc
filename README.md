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
| [01-executables.md](docs/01-executables.md) | `H.EXE` and the five helpers; the ACK-3D fingerprints; the parser keyword table; the debug strings that survived; `KIT.OVL`'s trig tables and font |
| [02-containers.md](docs/02-containers.md) | `.DTF` indexed chunks and `.RES`/`.TAB` named archives |
| [03-level-scripts.md](docs/03-level-scripts.md) | The commented ASCII level language, the object model, the type IDs |
| [04-maps.md](docs/04-maps.md) | The six 64×64 grids, the wall flag bits, the trailing record list, the 1040-byte hole |
| [05-graphics.md](docs/05-graphics.md) | GIF87a tiles, IFF-PBM backdrops, one palette for the whole game, the FLIC |
| [06-audio.md](docs/06-audio.md) | DIGPAK/MIDPAK, 19 Miles drivers, headerless `.SND`, XMIDI, The Fat Man's patch bank |
| [07-install-and-runtime.md](docs/07-install-and-runtime.md) | `INSTALL.DAT`, the generated batch files, the command line, the controls |
| [08-vs-ack3d.md](docs/08-vs-ack3d.md) | What came from the engine, what Deep River added, what neither uses |
| [09-easter-eggs-and-leftovers.md](docs/09-easter-eggs-and-leftovers.md) | Slob Zone, the stale level copy, the projectile pool, the SDK demo on the retail disc |
| [10-open-questions.md](docs/10-open-questions.md) | Everything unresolved, with the measurements behind it |
| [notes/level-inventory.md](notes/level-inventory.md) | All eleven containers, per-plane cell counts, shared assets |
| [notes/object-catalogue.md](notes/object-catalogue.md) | The full type table, the cast, the trash economy |
| [notes/phone-calls.md](notes/phone-calls.md) | The ten speech banks and what they reuse |

## Highlights

**It is an ACK-3D game, and the credits say so out loud.** `credits.gif`
lists "3D GRAPHICS …… LARY MYERS" — the author of ACK-3D, the tile-based
ray-caster published with source in *The Amazing 3-D Games Adventure Set*.
`H.EXE` still carries the engine's assertion strings naming `ACKVIEW.C`,
`ACKPOV.C` and `ACKLDBMP.C`, its 21-entry `ERR_*` table, and the two `$`-
terminated panic messages `Screw up in XRAY$` and `Screw up in YRAY$` from the
assembly caster.

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
`Slob Zone needs at least 3Mb free.`, both title screens ship on the disc, and
all ten between-level cutscene cards carry the **Slob Zone 3D** logo and never
the H.U.R.L. one.

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

**The wall flag bits decode from the data alone.** Wall cells above 255 are
`flags << 8 | slot`. All 307 cells with `0x10` name a door texture; 132 of the
142 cells with `0x50` land on exactly the slot the level gave to `RedDoor:`,
`GreenDoor:` or `BlueDoor:`; and all 1,321 cells with `0x08` are picket
fences, hedges, pole fences and shower curtains — every masked texture in the
game and nothing else.

**Six of the ten levels carry a fossil of the level compiler.** Each map chunk
has 1,040 unused bytes between the grids and the record list. In six files
they still hold a single tile index repeated hundreds of times — the tail of a
floor-plane fill the writer never cleared.

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
```

`<install>` is the directory holding `H.EXE` and the `*.DTF` files.

## Status

First pass. Chapter 10 lists what is still open — chiefly the exact role of
map plane 0 against the two wall grids, four unidentified wall flag bits, the
purpose of the 1,040-byte gap, how `God Mode!` is triggered, and the
1800-versus-1920 discrepancy between the trig tables and the level scripts.
Nothing in the other chapters depends on those answers.
