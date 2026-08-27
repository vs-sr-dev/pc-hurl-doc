# 06 — Audio

The game does not contain a sound engine. It contains **DIGPAK and MIDPAK**,
John W. Ratcliff's sound system from The Audio Solution, driving **Miles
Design AIL** music drivers, playing **XMIDI** through a **General MIDI patch
bank by The Fat Man**. All four are credited on `credits.gif`, and all four
are shipped as separate loadable files.

```sh
python tools/hurlaudio.py "<install>" xmi
python tools/hurlaudio.py "<install>" opl
python tools/hurlaudio.py "<install>" drivers
python tools/hurlaudio.py "<install>" snd   out/sfx
python tools/hurlaudio.py "<install>" banks out/speech
```

## `.SND` — sound effects with no header at all

46 files, 640,494 bytes. There is no header, no magic, no length and no
sample rate: a `.SND` is **raw unsigned 8-bit mono PCM**, silence being 0x80,
handed straight to DIGPAK's `DigPlay`, which takes the rate from the caller's
`SNDSTRUC`. The rate is therefore **not recoverable from the files** — the
tools default to 11025 Hz, which is DIGPAK's usual rate for this period and
gives plausible lengths (`TOILET.SND`, the longest at 80,726 bytes, becomes a
7.3-second flush).

`H.EXE` names 25 of them directly, including `Duckdone.snd`, `Pigchew.snd`,
`Twister.snd`, `cashreg.snd`, `dooropen.snd`, `Toilet.snd` and `Surrend.snd`.

Two small oddities in the set: `PIGBOUNC.SND` and `PIGHIT.SND` are
**byte-identical**, and the file the engine loads for a bouncing pig is
`PIOGBOU.SND` — with the `O` and the `G` transposed. There is also a
`PIGBOU2.SND`.

## The speech banks: ten telephone calls

`BOB1.RES` … `BOB10.RES` hold the game's dialogue, one archive per level,
addressed by the code as `bob%d`. Clip names encode speaker and scene:

| Prefix | Speaker |
|---|---|
| `bobp…` / `bob…` | Bob himself |
| `oper…` | the operator |
| `incw…` | the incinerator worker |
| `prin…` | the principal |
| `hamb…` | the burger clerk |

with a two-letter scene tag (`bs`, `tp`, `sc`, `ds`, `uf`, `ff`, `eg`) and a
two-digit take number: `bobpbs01.snd`, `operuf05.snd`, `incwds07.snd`.

Every bank except the tenth opens with the sound of the call connecting —
`pcoin.snd` (a payphone coin) in banks 1, 2 and 5, `bing.snd` in banks 3, 4
and 6–9.

| Bank | Clips | Total | Notes |
|---|---:|---:|---|
| BOB1 | 12 | 41.4 s | `bobpbs`/`operbs` |
| BOB2 | 10 | 35.6 s | `bobptp`/`opertp` |
| BOB3 | 11 | 43.1 s | `incwsc`/`bobpsc` |
| BOB4 | 10 | 47.0 s | `incwds`/`prinds` |
| BOB5 | 11 | 46.5 s | `bobpuf`/`operuf` |
| BOB6 | 16 | 58.8 s | `hambff`/`bobpff` |
| BOB7 | 15 | 61.5 s | shares 10 clips with BOB3 |
| BOB8 | 20 | 94.6 s | shares 9 with BOB4, 5 with BOB5 |
| BOB9 | 16 | 58.8 s | **the same 16 clips as BOB6, reordered** |
| BOB10 | 8 | 28.8 s | a different scheme entirely: `bobcall`, `bobsuds`, `bobmortl`, `bobnaked`, `bobhere`, `bobburp`, `boblook`, `bobfoot` |

`END.RES` adds `bobpeg01.snd` and `bobpeg02.snd`, and `INTRO.RES` carries 12
more clips (50.7 s), of which `qcut7.snd` and `qcut8.snd` are byte-identical.

Durations above assume 11025 Hz; at 22050 Hz halve them.

## Music: 18 XMIDI files

Standard Miles XMIDI — `FORM…XDIR/INFO` then `CAT …XMID`. Every game file
declares **one** sub-song.

| File | Bytes | Use |
|---|---:|---|
| `1.XMI` … `10.XMI` | 6,272–23,118 | the ten levels, loaded as `%d.xmi` |
| `INTRO.XMI` | 4,508 | the opening |
| `DEEPLOGO.XMI` | 2,450 | the Deep River logo |
| `MLOGO.XMI` | 1,262 | under `MLOGO.FLI` |
| `HURLCQ.XMI` | 452 | a 452-byte sting behind the title |
| `HURLLED.XMI` | 1,588 | level-end |
| `LOAD.XMI` | 13,884 | the loading screen |
| `FANFARE.XMI` | 15,760 | victory |
| `SETM.XMI` | 15,986 | **not the game's** — see below |

Three of the ten level tracks are byte-identical reuses: `7.XMI` = `3.XMI`,
`8.XMI` = `4.XMI`, `9.XMI` = `6.XMI`. Ten levels, seven pieces of music — and
the three that repeat are exactly the three levels whose speech banks also
repeat (BOB7≈BOB3, BOB8≈BOB4, BOB9=BOB6). The back half of the game reruns
the front half's audio.

`SETM.XMI` is the only file with **five** sub-songs, because it is the MIDPAK
SDK's demonstration music, shipped by accident
([09-easter-eggs-and-leftovers.md](09-easter-eggs-and-leftovers.md)).

## `FAT.OPL` — The Fat Man's patch bank

3,622 bytes, and the credits name it: *General MIDI patches © 1994 The Fat
Man and K. Weston Phelan*. "FAT" is the composer, George "The Fat Man"
Sanger, not an allocation table.

```
offset  size          contents
0       1086          { uint16 patch; uint32 offset; } dir[181]
1086    2             padding
1088    2534          181 patch records of 14 bytes
```

The 181 patches are **128 melodic** (numbers 0–127) plus **53 percussion**,
numbered `0x7F00 | note` for GM notes 35 through 87 — 32547 to 32599. Each
record is a flat 14 bytes, the usual two-operator OPL2 register set.

## Drivers

Both halves of the sound system are external and are chosen at install time by
`SETD.EXE` (digital) and `SETM.EXE` (music).

**21 DIGPAK/MIDPAK `.COM` drivers**, all `Written by John W. Ratcliff`:
Sound Blaster / Pro / 16 / clone, ProAudio Spectrum 8 and 16, Gravis
UltraSound, Adlib Gold, VESA, and `NOSOUND.COM`; four interchangeable MIDPAK
builds (`CMIDPAK`, `PMIDPAK`, `SMIDPAK`, `TMIDPAK`) that the installer copies
into place as `MIDPAK.COM`; `DIGAUTO.COM`, the 40 kB autodetect loader; and
`VECTOR.COM`, a 400-byte `REAL-MODE INTERUPT VECTOR TRAPPER` (spelled that way
in the file) that `H.EXE` names explicitly — the protected-mode game needs a
real-mode thunk to reach the drivers.

**19 Miles AIL `.ADV` drivers** with matching one-line `.ADD` descriptions,
`Copyright (C) 1991,1992 Miles Design, Inc.` — Ad Lib and Ad Lib Gold, Sound
Blaster FM in three flavours, AWE32, PAS 8/16, Gravis, MT-32/LAPC-1, Roland
Sound Canvas, Sierra Aria, Turtle Beach MultiSound, Tandy Sensation, Windows
Sound System, PC speaker, and two VESA drivers whose description string is
still the placeholder `to be determined...`.

Three of them are byte-identical to each other (`GENMID.ADV` = `MT32MPU.ADV` =
`SC32MPU.ADV`, and `SENSAT.ADV` = `WSS.ADV`) — the same driver shipped under
several names so the setup menu can list several cards.
