# Rescue and move progression corrections

The universal mission hook now spawns NPCs once. Four zones had a duplicate
segment hook; those copies are removed without changing encounter tables.
Nursery Courier places one Falcomon, Botamon, and Punimon together on floor 2.
Each must be rescued. Partial rescues persist, and only missing targets spawn
on a retry. A normal or secret-room route clear allows Clockmon's debrief;
escape, defeat, and unrelated dungeon clears do not.

For older accepted missions already marked rescued, Clockmon can recover the
missed clear from the engine's completed-dungeon record. Existing in-progress
floor layouts are not rewritten: leave and re-enter for corrected NPC spawns.

## Move-owned progression

Each existing move keeps its ID, learnset, targeting, animation, and implemented
effects. No character identity checks, species-specific rules, or duplicate
stage versions are introduced. The immutable Cyber Sleuth CSVs are unchanged.

| Earliest natural learning stage | Damage power | PP |
| --- | --- | --- |
| Rookie and lower | 20–39 | 20–29 |
| Champion / Armor | 40–59 | 30–39 |
| Ultimate | 60–79 | 40–49 |
| Mega / Ultra | 80–99 | 50–59 |

The added starter attacks remain 20 power / 20 PP. Source attack strength ranks
moves inside each band; weaker attacks receive more PP. Damaging moves have
100 accuracy or their existing guaranteed-hit behavior. Fixed-damage moves
use their band's damage amount; their defense bypass remains distinct from
ordinary power. Support moves retain their effects and gain their tier's PP.
Range and target shape retain their tactical roles, rather than making every
late melee attack hit the entire room.

There are 100 cross-stage moves in the existing source learnsets. These keep
the earliest learner's tier and remain shared exceptions, listed in
`DIGIMON_SHARED_MOVE_EXCEPTIONS.csv`. Common single-use TMs remain unrestricted;
learned moves are retained through Digivolution as before.

`python Scripts/digimon_playtest_repairs.py` reapplies the repairs and generates
`DataAsset/Digimon/move_balance.json`. The regular skill generator consumes this
move-owned policy, preventing a later regeneration from undoing the balance.
Rebuild the Skill index and Windows package after applying it.
