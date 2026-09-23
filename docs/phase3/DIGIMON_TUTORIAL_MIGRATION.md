# Training Maze teacher migration

The former early-route checkpoint tutorial has been removed from Forest Camp. Its actors are no longer unhidden, so the player cannot trigger the old guided tour. Accepting the child’s garden lead immediately preserves the existing garden completion state.

| Removed Forest Camp actor | Replacement on Training Maze entry floor (map ID 4 / displayed floor 5) | Lesson |
| --- | --- | --- |
| `Guide_1` | Tentomon | Observe the room and use distance or corners. |
| `Guide_2` | Hagurumon | Manage turns and avoid isolating a partner. |
| `Guide_3` | Gotsumon | Use items before a problem becomes a rescue. |
| `Guide_4` | Palmon | Keep the team together in a corridor. |
| `Guide_5` | Gomamon | Retreat, regroup, and return prepared. |
| `Guide_End` | Hawkmon | Mark discoveries so another team can return safely. |

| Removed dungeon teacher | Replacement on Training Maze entry floor (map ID 4 / displayed floor 5) | Lesson |
| --- | --- | --- |
| Tropical Jungle `TALK_ADVICE_NEUTRAL` | Patamon | Identify friendly map markers before approaching. |
| Tropical Jungle `TALK_ADVICE_EXP` | Koromon | Use techniques to earn experience. |
| Native Forest Trail `TALK_ADVICE_RECRUIT` | Gabumon | Scan data and restore a Digimon at the terminal. |
| Native Forest Trail `TALK_ADVICE_FADED` | Hawkmon | Mark route discoveries for the next team. |
| Native Forest Trail `AccuracyTalk` | Biyomon | Read accuracy and speed changes. |
| Panorama Cliffs `TALK_ADVICE_MISS` | Biyomon | Choose positions that reduce a miss’s risk. |
| Panorama Cliffs `PairTalk` pair 0/1 | Veemon | Use team controls, leader changes, and partner behavior. |
| Bramble Woods `TALK_ADVICE_POISON` | Wormmon | Manage poison without wasting turns. |
| Factorial Quarry `TALK_ADVICE_QUARRY` | Armadillomon | Compare map marks to find a hidden route. |
| Forsaken Desert `TALK_ADVICE_PYRAMID` | Armadillomon | Compare route reports to solve a path puzzle. |

The old Apricorn recruitment advice is deliberately replaced by scan restoration. All 13 instructors remain on the normally reachable entry floor. The automated resident test verifies that serialized teacher records are absent from installed zone data and their source generators, and that their replacement lessons are present on map ID 4.

Each replacement is an independent friendly, interactable actor placed on the Green Gym Maze entry floor (map ID 4 / displayed floor 5), the floor reached by normal dispatch. The segment's `ScriptZoneStep` calls `SpawnTrainingTeachers`, which uses the training map's `StairsMapGenContext`. They remain available on repeat visits and are not tied to a story clear. Gym Circuit’s target also uses map ID 4. Native checks verify all 13 teachers, their interaction actions, and walkable positions reachable from the entrance.
