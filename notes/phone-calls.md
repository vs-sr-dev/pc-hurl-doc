# The telephone calls

Ten `BOB*.RES` archives, one per level, holding the game's recorded dialogue.
The engine addresses them as `bob%d`, and the level scripts give every level a
`Phone:` wall slot for the telephone you use to trigger them.

```sh
python tools/hurlres.py   "<install>" list BOB1
python tools/hurlaudio.py "<install>" banks out/speech
```

## Naming

`<speaker><scene><take>.snd`, all lower case, 8.3.

| Speaker prefix | Who |
|---|---|
| `bobp…`, `bob…` | Bob |
| `oper…` | the operator |
| `incw…` | the incinerator worker |
| `prin…` | the principal |
| `hamb…` | the burger clerk |

Scene tags: `bs`, `tp`, `sc`, `ds`, `uf`, `ff`, `eg`. Take numbers are two
digits, `01` upward.

Every bank but the tenth opens with the call connecting: `pcoin.snd`, a
payphone coin, in banks 1, 2 and 5; `bing.snd` in banks 3, 4 and 6–9.

## Contents

| Bank | Clips | Length¹ | Members |
|---|---:|---:|---|
| BOB1 | 12 | 41.4 s | `pcoin`, `bobpbs01–06`, `operbs01–05` |
| BOB2 | 10 | 35.6 s | `pcoin`, `bobptp02–05`, `opertp01–05` |
| BOB3 | 11 | 43.1 s | `bing`, `incwsc01–05`, `bobpsc01–05` |
| BOB4 | 10 | 47.0 s | `bing`, `incwds01–05`, `prinds01–04` |
| BOB5 | 11 | 46.5 s | `pcoin`, `bobpuf01–05`, `operuf01–05` |
| BOB6 | 16 | 58.8 s | `bing`, `hambff01–11`, `bobpff01–04` |
| BOB7 | 15 | 61.5 s | `bing`, `bobpsc01–09`, `incwsc01–05` |
| BOB8 | 20 | 94.6 s | `bing`, `operuf01–05`, `incwds01–10`, `prinds01–04` |
| BOB9 | 16 | 58.8 s | `bing`, `bobpff01–04`, `hambff01–11` |
| BOB10 | 8 | 28.8 s | `bobcall`, `bobsuds`, `bobmortl`, `bobnaked`, `bobhere`, `bobburp`, `boblook`, `bobfoot` |

¹ at 11025 Hz; the `.SND` files store no rate
([docs/06-audio.md](../docs/06-audio.md)).

Plus `END.RES` — `bobpeg01.snd`, `bobpeg02.snd`, 11.1 s — and 12 clips in
`INTRO.RES` (`comqint1`, `comqint2`, `qcut2`…`qcut10`, `comqeg02`), of which
`qcut7.snd` and `qcut8.snd` are byte-identical.

## Reuse

**`BOB9` is `BOB6`.** Same sixteen clips, byte for byte, in a different
directory order. `BOB7` shares ten clips with `BOB3`, `BOB8` shares nine with
`BOB4` and five with `BOB5`. The three reused banks belong to levels 7, 8 and
9 — exactly the three levels whose music (`7.XMI`, `8.XMI`, `9.XMI`) is also a
byte-identical copy of an earlier level's.

Ten levels; seven scenes; seven pieces of music.

## Related sounds

Not part of the banks, but part of the same set piece — the loose `.SND` files
on the disc include `PDIALROT.SND` (98,429 bytes, a rotary dial),
`PDIALTT.SND` (56,542, touch-tone), `PRING.SND` (27,204), `PBUSY.SND`
(28,027), `PHANG.SND`, `PHANG2.SND` and `PCOIN.SND`. The vending machine and
the shower have their own: `CASHREG.SND`, `SHWR.SND`, and `TOILET.SND` at
80,726 bytes is the longest sound in the game.
