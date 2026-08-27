# 02 — The two container formats

The game stores everything in two archive formats, neither compressed and
neither obfuscated. Both are trivial, and both were clearly designed so that
the artists' files could be dropped in unchanged — the members are ordinary
GIFs, ordinary Deluxe Paint pictures and ordinary raw sound.

```sh
python tools/hurldtf.py "<install>" list LEV1
python tools/hurldtf.py "<install>" census
python tools/hurlres.py "<install>" list GRAPH
```

## `.DTF` / `.OVL` — indexed chunk container

Used by the eleven `LEV*.DTF` / `PICS.DTF` level files and by `KIT.OVL`.

```
offset  size  contents
0       2000  uint32 offset[500]      fixed-size directory
2000    ...   chunk 0
...           chunk 1, chunk 2, ...
```

The directory is always 500 slots, always 2000 bytes, and always exactly at
the start of the file. Entry *i* is the byte offset of chunk *i*; unused
slots are zero, and the **last used entry points one past the final chunk,
i.e. at end-of-file**, which is how a chunk's length is obtained. There are no
names, no types and no lengths — a chunk's identity is its index, and the
level script refers to art by index (`ScreenBack: 2`, `RedDoor: 5`, `1,46`).

Verified on all twelve containers: the last non-zero offset equals the file
size in every case.

Chunk layout is identical in all eleven level files:

| Chunk | Contents |
|---:|---|
| 0 | the level script, plain ASCII with `;` comments ([03](03-level-scripts.md)) |
| 1 | the map — six 64×64 grids plus a trailing list ([04](04-maps.md)) |
| 2 | `ScreenBack`: IFF `PBM ` 320×200, the HUD frame |
| 3 | `ScrollBack`: IFF `PBM ` 320×200, the horizon strip |
| 4 … | every wall and object bitmap, GIF87a, all 64×64 |

`KIT.OVL` uses four directory slots for three chunks and holds no images at
all ([01](01-executables.md)).

### Census

| File | Chunks | GIFs | Bytes |
|---|---:|---:|---:|
| `LEV1.DTF` | 185 | 181 | 460,352 |
| `LEV2.DTF` | 289 | 285 | 681,484 |
| `LEV3.DTF` | 242 | 238 | 567,152 |
| `LEV4.DTF` | 263 | 259 | 669,778 |
| `LEV5.DTF` | 231 | 227 | 595,684 |
| `LEV6.DTF` | 246 | 242 | 629,326 |
| `LEV7.DTF` | 281 | 277 | 665,368 |
| `LEV8.DTF` | 272 | 268 | 697,216 |
| `LEV9.DTF` | 239 | 235 | 609,386 |
| `LEV10.DTF` | 269 | 265 | 703,628 |
| `PICS.DTF` | 289 | 285 | 681,498 |
| `KIT.OVL` | 3 | 0 | 62,924 |

Each level file is **self-contained**: it carries its own copy of every
bitmap it needs, including the ones every level uses. Across the twelve
containers there are **2,762 GIF chunks but only 684 distinct images** — 75%
of the shipped tile data is duplication. That is the whole reason a game with
684 sprites needs a CD-ROM, and it is why the engine can load a level with one
`fopen` and one seek table.

`PICS.DTF` is not a resource file despite the name — it is a **stale copy of
level 2** ([09](09-easter-eggs-and-leftovers.md)).

## `.RES` + `.TAB` — named flat archive

Used for everything that is not a level: menus, cutscenes and speech.

`NAME.RES` is the payload, concatenated with no padding. `NAME.TAB` is the
directory: a bare array of 21-byte records, no header, no count.

```c
struct TabEntry {          /* 21 bytes, little-endian */
    char     name[13];     /* NUL-padded 8.3 name, with its extension */
    uint32_t offset;       /* into the .RES */
    uint32_t size;
};
```

The record is deliberately unaligned — `offset` starts at byte 13. The entry
count is `filesize / 21`, which divides exactly for all fourteen `.TAB` files,
and in every case the directory covers the `.RES` from byte 0 to its last byte
with no gaps and no overlap.

| Archive | Members | `.RES` bytes | Contents |
|---|---:|---:|---|
| `GRAPH` | 46 | 758,266 | menus, HUD, keys, title screens, credits |
| `INTRO` | 40 | 1,056,990 | the opening sequence: 28 pictures and 12 speech clips |
| `CUT` | 10 | 275,730 | `cut1.gif` … `cut10.gif`, the between-level cards |
| `END` | 2 | 122,330 | `bobpeg01.snd`, `bobpeg02.snd` |
| `BOB1` … `BOB10` | 8–20 | 317k–1,042k | per-level telephone dialogue ([06](06-audio.md)) |

Member names are the artists' and sound editors' original file names, extension
and all — `slobtitl.gif`, `buttdn1.gif`, `incwds07.snd`. Nothing was renamed
on the way into the archive.
