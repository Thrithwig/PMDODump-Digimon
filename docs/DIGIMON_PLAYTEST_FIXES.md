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

## Move redesign supersedes the original progression bands

The subsequent tactical move redesign replaces the earlier rigid damage/PP bands.
The current source is `DataAsset/Digimon/MoveRedesign/designs/*.json`. Its stage
power guides are approximately 25/35/45/55; shared moves use stage and learning-level
access, while geometry, accuracy, effects, and PP provide the tactical tradeoffs.
All PP is capped at 30, with a median near 20. The added starters remain 20/20.

See [the redesign report](DIGIMON_MOVE_REDESIGN.md) for counts, examples, exceptions,
and validation. Use `python Scripts/digimon_move_designs.py` to regenerate only
move assets, then rebuild the Skill index. `digimon_move_balance.py` now produces
a compatibility report from those designs; it cannot restore the obsolete bands.
Mission behavior documented above is unchanged by the move redesign.
