# Level inventory

Regenerate with:

```sh
python tools/hurldtf.py "<install>" census
python tools/hurlinf.py "<install>" header
python tools/hurlmap.py "<install>" info
python tools/hurlmap.py "<install>" shared
python tools/hurlmap.py "<install>" objects LEV1
```

## Per file

Cell counts are non-zero cells out of 4,096. The six grids are the six `fread`
calls in `AckReadMapFile` ([docs/04-maps.md](../docs/04-maps.md)).

| File | Bytes | Chunks | GIFs | Walls | Objects defined | Objects placed | map | xGrid | yGrid | floor | ceiling | Records |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LEV1 | 460,352 | 185 | 181 | 52 | 104 | 76 | 747 | 691 | 722 | 4096 | 90 | 21 |
| LEV2 | 681,484 | 289 | 285 | 103 | 158 | 130 | 1093 | 1008 | 1068 | 4096 | 313 | 5 |
| LEV3 | 567,152 | 242 | 238 | 52 | 120 | 108 | 1202 | 1367 | 1373 | 4096 | **4096** | 10 |
| LEV4 | 669,778 | 263 | 259 | 72 | 119 | 97 | 1225 | 1163 | 1263 | 4096 | 1328 | 5 |
| LEV5 | 595,684 | 231 | 227 | 58 | 130 | 115 | 1158 | 1009 | 1142 | 4096 | 378 | 10 |
| LEV6 | 629,326 | 246 | 242 | 57 | 175 | 150 | 1066 | 1108 | 1133 | 4096 | 2948 | 10 |
| LEV7 | 665,368 | 281 | 277 | 52 | 130 | 88 | 948 | 943 | 1026 | 4096 | **4033** | 10 |
| LEV8 | 697,216 | 272 | 268 | 73 | 122 | 105 | 1271 | 1220 | 1226 | 4096 | 699 | 5 |
| LEV9 | 609,386 | 239 | 235 | 59 | 170 | 116 | 933 | 969 | 982 | 4096 | 504 | 10 |
| LEV10 | 703,628 | 269 | 265 | 52 | 155 | 129 | 897 | 930 | 930 | 4096 | 874 | 18 |
| PICS | 681,498 | 289 | 285 | 103 | 158 | 125 | 1093 | 1008 | 1068 | 4096 | 313 | 5 |

`PICS` is a stale copy of level 2, not an eleventh level.

**The floor is complete in every level** — all 4,096 cells, with four to
twenty-five distinct tiles. The ceiling is what varies, and **levels 3 and 7
are roofed**: 4,096 and 4,033 cells against 90 in the outdoor level 1. Those
two are also the only levels whose scripts set `TopColor: 0` instead of the
sky blue 174, and their wall textures (`CLASS-1.GIF`, `LOCKER2/4.GIF`,
`LIBRARY4.GIF`, `HAPYDOOR.GIF`, `SEWER-2.GIF`) say school and sewer.

## Records

Nine of the eleven files contain only the copied template records. Only LEV1
(11 of its 21) and LEV10 (8 of 18) add any of their own.

| File | Records | Boilerplate | Its own |
|---|---:|---:|---:|
| LEV1 | 21 | 10 | 11 |
| LEV10 | 18 | 10 | 8 |
| LEV3, LEV5, LEV6, LEV7, LEV9 | 10 | 10 | 0 |
| LEV2, LEV4, LEV8, PICS | 5 | 5 | 0 |

## Rare wall flags

61 cells in the whole game use the multi-height path, and 9 the sliding-wall
one:

| Level | Flag | Cells | Textures |
|---|---:|---:|---|
| LEV8 | `0x02` | 25 | `LOCKER2/3/4.GIF`, `CLASS-1*.GIF` |
| LEV10 | `0x02` | 32 | `wall2.gif`, `wall2b.gif` |
| LEV10 | `0x04` | 4 | `marb1a.gif`, at the four corners of one block |
| LEV2 | `0x20` | 4 | `sidetile`, two adjacent `hedge` |
| LEV4 | `0x20` | 3 | `SIDETILE.GIF`, two adjacent `LIBRARY4.GIF` |
| LEV10 | `0x20` | 2 | two adjacent `trlr-5h.gif` |
| LEV5 | `0x18` | 2 | two adjacent `door3.GIF` (a see-through door) |

## Shared assets

| Asset | Shared by |
|---|---|
| `ScreenBack` (chunk 2) | identical in all eleven files |
| `ScrollBack` sky A | LEV1, LEV5, LEV8 |
| `ScrollBack` sky B | LEV6, LEV10 |
| `ScrollBack` sky C | LEV2, LEV3, LEV4, LEV7, LEV9, PICS |
| music | `7.XMI`=`3.XMI`, `8.XMI`=`4.XMI`, `9.XMI`=`6.XMI` |
| speech | `BOB9` = `BOB6` (same 16 clips, reordered); `BOB7` shares 10 with `BOB3`; `BOB8` shares 9 with `BOB4` and 5 with `BOB5` |

2,762 GIF chunks across the eleven containers, **684 distinct** — 75 %
duplication, because every level file is self-contained.

## Level 1 in ASCII

`python tools/hurlmap.py "<install>" ascii LEV1 0` — the trailer park, with
the sealed projectile-pool room in the top-left corner (rows 1–10, columns
1–8) and the bus at rows 29–40:

```
 0 ################################################################
 1 #........#.....................................................#
 2 #........#.....................................................#
 …
11 ##########.....................................................#
…
29 #........................########################..............#
30 #........................##....##.##....##......#..............#
31 #........................##.#.##@........#......##.............#
…
63 ################################################################
```

`#` is a wall slot below 256, `@` a cell with flag bits set — a door, a locked
door, a sliding wall or a see-through wall
([docs/04-maps.md](../docs/04-maps.md)).
