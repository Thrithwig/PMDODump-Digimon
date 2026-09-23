# Rescue destination repair — 2026-09-17

Dragon Eye Current incorrectly targeted zero-based floor 9 (displayed floor 10), the fixed `end_depleted_basin` reward map. Its room-based rescue spawn step could not place Seadramon there. The quest now targets zero-based floor 8 (displayed floor 9).

Story.ensure refreshes incomplete native mission destinations from authored definitions without resetting rescue progress. Mission generation calls it before matching destination floors. Existing accepted quests therefore migrate on the next generated expedition. An already-generated floor in a running game is not retroactively changed.

At the user's direction, removed the optional Gym Circuit rescue dispatch. Green Gym remains a tutorial area with its original access and all 13 teachers. Existing pending Gym Circuit entries are retired at Clockmon interaction or mission generation, while historical completion counts remain intact.

Validation:
- 15 Python tests passed, including Lua scenarios for save migration and all 20 main / 17 optional completions.
- All 37 remaining rescue destinations audited against installed map generator types.
- Native dungeon check passed across 567 floors, with Dragon Eye Current accepted using the old floor value. It verifies exactly one interactable Seadramon on floor 9 and none on other floors, plus the existing training-teacher checks.
- Full solution build: zero errors. Windows publish succeeded. Published Lua files match source hashes.

The player must restart the updated build and generate a new Dragon Eye Basin run if floor 9 was already visited in the current expedition. No fresh save is needed.
