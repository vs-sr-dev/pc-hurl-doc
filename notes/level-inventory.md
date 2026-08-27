# Level inventory

Regenerate with:

```sh
python tools/hurldtf.py "<install>" census
python tools/hurlinf.py "<install>" header
python tools/hurlmap.py "<install>" info
python tools/hurlmap.py "<install>" objects LEV1
```

## Per file

| File | Bytes | Chunks | GIFs | Walls declared | Objects defined | Objects placed | Wall cells | Floor cells | Ceiling cells | Map records |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LEV1 | 460,352 | 185 | 181 | 52 | 104 | 76 | 747 | 3,693 | 610 | 21 |
| LEV2 | 681,484 | 289 | 285 | 103 | 158 | 130 | 1,093 | 3,640 | 833 | 5 |
| LEV3 | 567,152 | 242 | 238 | 52 | 120 | 108 | 1,202 | 3,722 | **4,096** | 10 |
| LEV4 | 669,778 | 263 | 259 | 72 | 119 | 97 | 1,225 | 3,699 | 1,796 | 5 |
| LEV5 | 595,684 | 231 | 227 | 58 | 130 | 115 | 1,158 | 3,653 | 898 | 10 |
| LEV6 | 629,326 | 246 | 242 | 57 | 175 | 150 | 1,066 | 3,664 | 3,035 | 10 |
| LEV7 | 665,368 | 281 | 277 | 52 | 130 | 88 | 948 | 3,661 | **4,033** | 10 |
| LEV8 | 697,216 | 272 | 268 | 73 | 122 | 105 | 1,271 | 3,731 | 1,163 | 5 |
| LEV9 | 609,386 | 239 | 235 | 59 | 170 | 116 | 933 | 3,675 | 968 | 10 |
| LEV10 | 703,628 | 269 | 265 | 52 | 155 | 129 | 897 | 3,640 | 1,394 | 18 |
| PICS | 681,498 | 289 | 285 | 103 | 158 | 125 | 1,093 | 3,640 | 833 | 5 |

`PICS` is a stale copy of level 2, not an eleventh level.

The grid is always 64 × 64 = 4,096 cells. The floor is 89–91 % covered in
every level; the ceiling is what varies, and **levels 3 and 7 are fully
roofed** — the two levels whose scripts also set `TopColor: 0` instead of the
sky blue 174. Those are the indoor levels, and their wall textures
(`CLASS-1.GIF`, `LOCKER2/4.GIF`, `LIBRARY4.GIF`, `HAPYDOOR.GIF`) say school.

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
door or a see-through wall ([docs/04-maps.md](../docs/04-maps.md)).
