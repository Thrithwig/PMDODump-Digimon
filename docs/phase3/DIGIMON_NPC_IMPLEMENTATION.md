# Storyboard resident implementation

Implemented against the user's updated `DIGIMON_STORYBOARD.md`, copied into this directory on 2026-09-15. The storyboard remains the design document; this file distinguishes installed behavior from later mission work.

## Installed

- 178 resident bindings across the ten settlement/interior maps and four dungeon endpoint maps. All 51 authored speaking roles have a binding. Supporting roles use fixed Digimon identities; the two Post House clerks are Quill and Stamp, distinct from the rescued Falcomon.
- Mamemon opens boxes, Sunflowmon is the Forest Camp guide, Gatomon/Nyaromon occupy the parent/child roles, Monzaemon guards the storehouse, and Unimon is the summit technician. Original entity IDs remain intact for native scripts and saved maps.
- The authored before/after conversations are stored in `DataAsset/Digimon/story_npcs.json`. `Scripts/digimon_story_npcs.py` compiles the installed Lua catalog. Nothing chooses a player-dependent or random resident species.
- Existing map characters are converted in their `.rsground` assets and also on map entry, so cached older maps receive the updated identity. Scripted replacement forms and native sidequest client/target IDs use Digimon too.
- Existing shops, exchange recipes, move tutoring, juice services, storage, assembly, quest rewards and travel handlers remain callable. Plain conversation handlers use the new dialogue; handlers with native service/quest work retain that work. Completed authored rescue clients do not reopen unrelated legacy conversations. The old Monzaemon confrontation is now described as a voluntary safety challenge, with retry and relief afterward.
- Pokémon terminology and temporary author notes were removed from the covered dialogue resources. Mamemon's service text describes careful charges and protecting the contents. Three old NPC Apricorn gifts now use existing HP Capsule A / Full Revival Spray items; reward timing is unchanged.

## Progression visible now

| Resident | Trigger | Visible result |
|---|---|---|
| Guardromon | Native Tropical Path clear, or an existing Tropical debrief | Arrives in Base Camp's clearing. No rescue record is fabricated. |
| Falcomon, Botamon, Punimon | `DigimonStory_TropicalPath.debriefed` | Appear together in town; the babies use the existing Sleep animation. An incomplete rescue or clear alone is insufficient. |
| Clockmon and local helpers | Tropical debrief / relevant local route completion | Authored greetings change; Clockmon shifts into the dispatch clearing and other residents move to reserved resting positions. |
| Flint | `DigimonStory_FaultlineRidge.debriefed` | Returns to Base Camp in the former survey/steel slot. |
| Impmon | `DigimonStory_TricksterWoods.debriefed` | Returns to Forest Camp. |
| Monzaemon | `forest_camp.SnorlaxPhase >= 4` | Rests away from the doorway; the supply workers can use the storehouse. Talking again does not restart the challenge. |
| Guardromon, late preparation | Freezeland's existing exposition flag | Leaves Base Camp and appears at the final camp. |

Positions are pixel coordinates in the existing 8-pixel ground grid. `DIGIMON_NPC_BINDINGS.csv` lists every binding, trigger, before position and resting position. Resting locations are checked against terrain and each other; arrivals avoid existing objects and entry markers. Counter staff retain their service positions. NPCs are refreshed after interaction and on map entry, not every frame.

## Later chapters and limits

The game currently implements only the first three primary rescue requests. This change does **not** pretend that the other storyboard rescues or Demon Lord encounters have been implemented. Their authored dialogue and placements are ready, but their grateful aftermaths require a real debrief record:

```lua
SV.Digimon.StoryMissions.records[zone_id] = { debriefed = true }
-- Or a future mission record may carry { zone = zone_id, debriefed = true }.
```

Only the mission's successful resolution/debrief code should write that record. An ordinary completed-dungeon entry does not substitute for a named rescue. An early Guildmaster Trail clear therefore does not trigger the finale speeches. The old forest child's illness/cure flags are deliberately not treated as the proposed Tiny Tunnel rescue.

The September 16 review removes legacy conversational fall-through for converted residents. Native services retain their transaction/menu callbacks with explicit Digimon dialogue templates; Clockmon and Falcomon have explicit service dispatch. Obsolete narrative callbacks are not invoked after the authored resident lines. New rescue visitors remain absent until their own debrief; existing contacts can remain present under their native schedules and give their before dialogue. Aquilamon leaves its early camp slot when the later rescue return activates its Misty Shelter placement.

English storyboard lines are used for the new conversations. Existing translated resource menus are preserved, but this is not a new translation of the story. The developer test grounds are outside the story-camp cast pass.

## Save and validation

No new save fields, save reset, party changes or submodule pin changes are required. Visibility, names and positions are derived from existing flags. Added residents are created only when absent from a loaded map; repeated entry reuses them. They are map residents, never scan recruits or assembly members.

Validation includes Lua state/migration/service scenarios, native loading of all 178 bindings and their art, native creation of the nursery group with live interaction handlers and animations, terrain/position checks, resource checks, and the full solution build. See [the September 16 review](PLAYTEST_REVIEW_2026_09_16.md) for the latest combined validation and playtest limits. Two existing Python sprite-source tests require an ignored `SpritePackages/Packages` directory absent from this checkout; installed game art is present and checked natively.

Regenerate the catalog after editing the source JSON:

```powershell
python Scripts/digimon_story_npcs.py
dotnet build PMDOData.sln --no-restore
```

Do not rerun the one-time bootstrap scripts in the untracked workspace `work` directory; the reviewed JSON and installed map/script edits are the source for this implementation.
