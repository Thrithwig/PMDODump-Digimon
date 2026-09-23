# Digimon project documentation

Start with [current status and next steps](PROJECT_STATUS.md).

The [workspace cleanup report](WORKSPACE_CLEANUP_2026_09_22.md) explains the two active copies, verified recovery archives, and documentation publication scope.

| Subject | Source of guidance |
|---|---|
| Conversion scope and pipeline | [Conversion plan](DIGIMON_CONVERSION_PLAN.md), [Data pipeline](DIGIMON_DATA_PIPELINE.md) |
| Story and routes | [Storyboard](phase3/DIGIMON_STORYBOARD.md), `phase3/storyboard_routes.json` |
| Dungeons, residents and tiles | [Dungeon implementation](phase3/DIGIMON_DUNGEON_IMPLEMENTATION.md), [NPC implementation](phase3/DIGIMON_NPC_IMPLEMENTATION.md), [Tile review](phase3/TILESET_PAIR_REVIEW.md) |
| Moves, matchups and progression | [Move redesign](DIGIMON_MOVE_REDESIGN.md), [Matchups](DIGIMON_DAMAGE_MATCHUPS.md), [Experience](DIGIMON_EXPERIENCE.md), [Retention](DIGIMON_STAT_RETENTION.md), [Training](DIGIMON_TRAINING.md) |
| Items and families | [Family types](DIGIMON_FAMILY_TYPES.md), [Family items](DIGIMON_FAMILY_ITEMS.md), [Key items](DIGIMON_KEY_ITEMS.md), [Loot](DIGIMON_LOOT_TUNING.md) |
| Visual testing | [Runbook](playtesting/TEST_CAMP_PILOT_RUNBOOK.md), [Adapter protocol](playtesting/PLAYTEST_FILE_ADAPTER_PROTOCOL.md), [Coverage](playtesting/VISUAL_COVERAGE_PLAN.md) |
| Transferring lab changes | [Review manifest](playtesting/TRANSFER_REVIEW_MANIFEST.md), [Copy-back procedure](playtesting/COPY_BACK_WORKFLOW.md) |

The dated repair reports and original design brief are historical evidence. Use current code and PROJECT_STATUS for implementation state. Repeated playtest handoffs/audits have been condensed into PROJECT_STATUS; their old paths are retained as pointers and exact originals are archived locally.
