# 00 — Overview

## The game

**H.U.R.L.** — Deep River Publishing, 1995, for Millennium Media Group, Inc.
A first-person, 256-colour, tile-based shooter for MS-DOS in which a boy in a
trailer park throws water balloons, bars of soap and cans of deodorant at
cartoon animals while picking litter up off the floor for pocket money.

The copyright block linked into `H.EXE` at `0x2ada0` reads, verbatim:

```
                              H.U.R.L.
(c)1995 Millennium Media Group,Inc. & Deep River. All Rights Reserved.
                Program (c) 1995 Deep River Publishing, Inc.
       H.U.R.L. is a trademark of Millennium Media Group,Inc.
```

`DISK.ID` gives the version: `H.U.R.L. / 1.0 / Disk Number 1`.

## The credits, as the game prints them

`credits.gif` in `GRAPH.RES` is a single 320×200 picture. It reads:

| Role | Name |
|---|---|
| 3D Graphics | **Lary Myers** |
| Artwork | Andy Hunter |
| Programmer | Ken Lemieux |
| Audio | Michael McInnis |
| Special thanks | Tom Tracy, Tom Yamartino, Bill Gray, Erik Antleman |

with two further lines in small type:

* *General MIDI patches © 1994 The Fat Man and K. Weston Phelan*
* *Sound Routines Provided by Midpak, Digpak — John W. Ratcliff*

and a `© 1994 Deep River Publishing` notice — a year earlier than the one in
the executable.

"3D Graphics — Lary Myers" is not a courtesy. Myers wrote **ACK-3D**, the
tile-based ray-caster published with *The Amazing 3-D Games Adventure Set*
(Coriolis, 1995), and H.U.R.L. is an ACK-3D game: `H.EXE` still carries the
engine's assertion strings naming `ACKVIEW.C`, `ACKPOV.C` and `ACKLDBMP.C`,
its `ERR_*` table, and the two panic strings `Screw up in XRAY$` and
`Screw up in YRAY$` from the assembly caster. See
[08-vs-ack3d.md](08-vs-ack3d.md).

## The other name

The game was built as **Slob Zone 3D**, and the disc never fully covers its
tracks. The game's own source file is `slob.c`; the out-of-memory message is
`Slob Zone needs at least 3Mb free.`; the title art ships in both brandings
(`slobtitl.gif` and `hurl.gif`); and every one of the ten between-level
cutscenes in `CUT.RES` carries the **Slob Zone** logo, not the H.U.R.L. one.
[09-easter-eggs-and-leftovers.md](09-easter-eggs-and-leftovers.md) collects
the evidence.

## Build chain

| Component | Evidence |
|---|---|
| Watcom C/C++, 32-bit protected mode | `WATCOM C Run-Time system code…` in `H.EXE`, `WATCOM patch level` |
| Rational Systems DOS/4GW extender | `LE` image at `0x2a88`, `RATIONAL DOS/4G`, `DOS4GW.EXE` on the disc |
| ACK-3D 3-D engine | `ACKVIEW.C` / `ACKPOV.C` / `ACKLDBMP.C`, `Screw up in XRAY$` |
| DIGPAK + MIDPAK sound system | `The Audio Solution, Copyright (c) 199x / Written by John W. Ratcliff` in 21 `.COM` drivers |
| Miles Design AIL music drivers | `Copyright (C) 1991,1992 Miles Design, Inc.` in 19 `.ADV` files |
| Knowledge Dynamics "The Installer" | `INSTALL Ver … Copyright (c) 1987-1994 / Knowledge Dynamics Corp` in `INSTALL.EXE` |
| Borland C++ 1991 | the three sound-setup programs |
| Microsoft C | `INSTALL.EXE` and the DOS/4GW stub |
| Deluxe Paint II Enhanced | `CRNG`, `GRAB` and `TINY` chunks surviving in the IFF-PBM art |

## File inventory

179 files, 16.5 MiB, all stamped 24 December 1996 in the copy examined.

| Ext | Files | Bytes | What it is |
|---|---:|---:|---|
| `.DTF` | 11 | 6,960,872 | level containers — script, map, backdrops and every tile ([02](02-containers.md)) |
| `.RES`+`.TAB` | 14+14 | 7,907,735 | flat archives — menus, cutscenes, phone-call speech ([02](02-containers.md)) |
| `.SND` | 46 | 640,494 | headerless 8-bit mono sound effects ([06](06-audio.md)) |
| `.XMI` | 18 | 219,192 | Miles XMIDI music ([06](06-audio.md)) |
| `.COM` | 21 | 174,455 | DIGPAK / MIDPAK loadable drivers |
| `.ADV`+`.ADD` | 19+17 | 302,490 | Miles AIL music drivers and their description files |
| `.EXE` | 6 | 783,798 | game, extender, installer, three sound-setup programs ([01](01-executables.md)) |
| `.OVL` | 1 | 62,924 | `KIT.OVL` — trig tables, cosine table, the font ([01](01-executables.md)) |
| `.FLI` | 1 | 233,149 | the animated Millennium Media Group logo ([05](05-graphics.md)) |
| `.OPL` | 1 | 3,622 | `FAT.OPL`, The Fat Man's FM patch bank ([06](06-audio.md)) |
| everything else | 9 | 21,224 | readme, installer script, `.BAT`, `.DES`, `.NFO`, `.LOG`, `.VMC`, `.ID` |

## Provenance of the copy examined

The directory analysed here is a hard-disk copy of the CD-ROM, and it is **not
pristine**: it contains `DYNAMIX.NFO`, a warez-scene release note from a group
calling itself Dynamix (no relation to the Sierra studio), headed
`HURL FULL CD RIP (c) MILLENNIUM MEDIA CORP`, supplied 05/10/95, packaged as
nine disks. That file was added by whoever ripped the disc; nothing else in
the directory references it, and no game code opens it.

Everything documented here is reproducible from a legitimate copy of the game.
The one place the provenance matters is `MEMCHECK.LOG` — a one-line log
(`MemCheck V3.0 Active (License: Deep River Publishing)`) written *by a run of
the game*, not shipped on the disc — and the file timestamps, which are
uniform and therefore meaningless.

## What is documented, and what is not

This repository documents the **retail DOS release, version 1.0**. There is no
attempt here to port, rebuild or re-implement the game — the goal is a
description of the file formats and of what the shipped data reveals about how
the game was made.

No game asset, no extracted art and no executable code is committed. The
programs in [`tools/`](../tools/) reproduce every table and figure from your
own copy.
