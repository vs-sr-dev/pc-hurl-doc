# Object catalogue

Every object in the game is declared in a level script, with a type ID and —
because the designers commented their files — a label. Regenerate with:

```sh
python tools/hurlinf.py "<install>" types
python tools/hurlinf.py "<install>" objects LEV1
```

## The cast

`charscrn.gif` in `GRAPH.RES` introduces eight characters. Each maps onto
exactly one type ID:

| Screen name | Type | Script label | Definitions |
|---|---:|---|---:|
| Ricochet Pig | 1 | `PIG` | 70 |
| Quack Attacker | 2 | `DUCK` | 51 |
| Sour Puss | 3 | `CAT` | 33 |
| Trash Twister | 4 | `TRASH TWISTER 1…4` | 22 |
| Swamp Breath | 14 | `GATOR` | 20 |
| **Bob the Slob** | 16 | `BOB THE SLOB` | **1** |
| Baboon Spittoon | 17 | `MONKEY` | 24 |
| Bug Eye Frog | 18 | `FROG` | 40 |

Bob is defined once in the entire game.

## The full type table

| ID | Definitions | Labels |
|---:|---:|---|
| 1 | 70 | PIG |
| 2 | 51 | DUCK (and `duck- 1`, `new duck- 1`) |
| 3 | 33 | CAT (and `CAT-new 1/2`) |
| 4 | 22 | TRASH TWISTER 1–4 |
| **5** | **249** | WATER BALLOON, FLY, KITTY LITTER, DUCK EGG, BANANA SPIT, SMOKE RING |
| 6 | 45 | BAR OF SOAP |
| 7 | 45 | DEODORANT |
| 8 | 22 | RAINCOAT |
| 9 | 22 | UMBRELLA |
| 10 | 22 | MOIST TOWELETTE |
| 11 | 11 | RED key |
| 12 | 11 | BLUE KEY |
| 13 | 11 | GREEN KEY |
| 14 | 20 | GATOR |
| 15 | 10 | SOAP-X 1–4 |
| 16 | 1 | BOB THE SLOB |
| 17 | 24 | MONKEY |
| 18 | 40 | FROG |
| 19 | 6 | HYDRANT WET / SPILLING |
| 20 | 11 | TOILET, TOILUP |
| — | — | *21–128 unused* |
| 129 | 180 | EMPTY CAN 1 / 2 / 3 |
| 130 | 180 | BANANA, NEWPAPER, BONE, DRIPPING SLIME |
| 131 | 239 | APPLE CORE, CEREAL BOX, TRASHCAN, BURGER SIGN, CAKE SIGN |
| 132 | 34 | TRASHCAN, STATUE, REFRIGERATOR, EZ CHAIR, SINK |
| 134 | 30 | SHRUB, CACTUS, TREE1, TREE2, HYDRANT DRY, MAILBOX |
| 135 | 55 | TREE-1, TREE-2, shrub, haystack, scarecrow, EZCHAIR |
| 137 | 4 | PHONE BOOTH 1 / 2 |
| 138 | 4 | PHONE ON TABLE 1 / 2 |
| 140 | 6 | SHOWER |
| 141 | 4 | BATH SINK |
| 142 | 5 | TOILET, BATH SINK |
| 144 | 6 | REFRIG |
| 145 | 8 | EZCHAIR |
| 146 | 8 | MAILBOX |
| 147 | 36 | DRIPPING SLIME, LAVA LAMP, FIRE HYDRANT NOT SPILLING |
| 148 | 8 | TABLE WITH VASE 1–4 |
| 149 | 8 | FLOOR LAMP 1–4 |

Unused within the scenery range: 133, 136, 139, 143.

## The economy

`trshscrn.gif` prices eight pieces of litter, and the prices fall into the
three litter types exactly:

| Price | Items | Type |
|---:|---|---:|
| 5¢ | crushed can, green bottle, purple bottle | 129 |
| 10¢ | banana peel, bone, newspaper | 130 |
| 25¢ | apple core, cereal box ("Pop") | 131 |

Types 130 and 131 also cover a little scenery (dripping slime, trashcans, shop
signs), so the type alone is not the price — but no priced bitmap lands in the
wrong bucket.

The same screen lists the three defences, which are types 8, 9 and 10:
raincoat, umbrella and moist towelette ("WIPE AWAY").

## Type 5 is "projectile"

Every thrown thing in the game shares one type: the player's water balloon,
the frog's fly, the cat's kitty litter, the duck's egg, the monkey's banana
spit and the gator's smoke ring. That is 249 of the 1,541 definitions in the
game, and all of them are parked off the edge of the map at level load
([docs/09-easter-eggs-and-leftovers.md](../docs/09-easter-eggs-and-leftovers.md)).

## State shapes

Each object has `Create`, `Destroy`, `Walk` and `Attack`; the eight named
characters also have `Interact`. Each state is `flags, views,
bitmaps-per-view, list`.

| views × per-view | Occurrences | What it is |
|---|---:|---|
| 1 × 1 | 3,937 | one still frame |
| 1 × 4 | 736 | a 4-step loop |
| **8 × 4** | 666 | 8 rotation views × 4 walk frames — the animals |
| 1 × 6 | 481 | the standard 6-step destruction burst |
| 1 × 8 | 267 | an 8-step loop |
| 1 × 16, 1 × 5, 1 × 3, 1 × 12, 1 × 32 | 80, 51, 47, 44, 40 | longer one-offs |

Frames are listed in pairs (`21,21,22,22`) to halve the rate — the format has
no other timing control.
