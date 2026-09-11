# PMDO to Digimon conversion proposal

Phase 2 Part 1 runtime and item-conversion status: see [DIGIMON_PHASE2.md](DIGIMON_PHASE2.md).

## Agreed scope

Convert the base PMD: Origins campaign into a Digimon dungeon crawler while retaining
the proven turn-based exploration engine.

The release criteria are:

* every playable character, partner, enemy, boss, shopkeeper, town NPC, rescue target,
  cutscene actor, and scripted creature spawn resolves to a Digimon;
* party members can digivolve and dedigivolve through branching lines;
* defeated hostile Digimon provide recoverable species data and never join directly;
* a teammate can be created only after its species data has been restored;
* only new saves are supported; no Pokemon-era save conversion will be built;
* a single static 2D image per Digimon is acceptable through Phase 3; complete sprites,
  portraits, and animation sets are deferred to Phase 4; and
* audio is outside the conversion scope, as are temporary battle digivolutions.

In player-facing text, an incomplete species code is **Scan Data** and a restored code
is a **DigiCode**. “Codebase” remains the design shorthand, not the UI term.

## Repository findings and boundaries

This repository generates PMDO data rather than containing the complete game.
`DataGenerator/Program.cs` dispatches generation, reserialization, string, and dump
operations. `MonsterInfo` currently reads 1,011 Pokemon from
`DataAsset/Monster/pokedex.9.sqlite`, calculates Pokemon evolution and join rates,
and emits `MonsterData`. Zone and map generators contain literal `MonsterID` species
references, while moves, traits, items, statuses, strings, maps, and encounters are
generated independently.

The populated pinned submodules provide:

* `PMDC` contains the gameplay layer and RogueEssence engine;
* `DumpAsset` contains serialized assets, maps, and Lua scripts; and
* `RawAsset` contains source visuals.

The local baseline now restores, builds, publishes, and launches successfully.
The imported dataset pipeline is implemented in this parent repository. Runtime
Scan Data, graph transitions, save rules, and converted content remain future work.
Engine additions should be generic graph-transition and post-defeat-reward services;
Digimon-specific policy should remain in generated data and scripts. Explain any
required submodule source changes before editing; preserve pins and `.gitmodules`.

## Authoritative source data

Use Liane Brisebois's **Digimon Cyber Sleuth Dataset** on Kaggle as the sole gameplay
data source for this conversion:

<https://www.kaggle.com/datasets/lianebrisebois/digimon-cyber-sleuth-dataset>

The required tables are exactly:

1. `Digimon.csv`
2. `Digivolution Requirements.csv`
3. `Digivolutions.csv`
4. `Skills by Digimon.csv`
5. `Skills.csv`

Do not scrape a Digimon wiki to fill gaps silently. Record a dataset version/download
date and checksum in release metadata. The Kaggle tables describe Cyber Sleuth, not
PMDO balance: preserve their facts in normalized `source` fields, then put intentional
PMDO overrides (damage, range, growth, scan cost, release status, and story role) in a
separate reviewed overlay. This distinction makes upstream refreshes auditable.

The repository now includes `Scripts/digimon_dataset.py`, a standard-library importer
that requires all five tables, normalizes stable IDs, builds forward and reverse
digivolution links, attaches requirements and learnsets, rejects dangling references,
and emits deterministic JSON. The five user-supplied CSVs are now preserved byte-for-byte in
`DataAsset/Digimon/Source`; the importer performs no network access. Run it after manually accepting Kaggle's terms and downloading the data:

```bash
python Scripts/digimon_dataset.py \
  --input /path/to/unpacked-dataset \
  --output DataAsset/Monster/digimon_manifest.json
```

The importer supports the supplied semicolon headers, level 1/50/99 source stats,
terminal `N/A` rows, and audited name corrections. Conflicting skill definitions
remain explicit variants; the selected roster cannot contain unresolved assignments.
SHA-256 hashes pin all five files. The original download date and publisher version
are unknown and recorded as null, rather than inferred from filesystem timestamps.
See `docs/DIGIMON_DATA_PIPELINE.md` for regeneration and test commands.

## Product and data decisions

### Roster

Start with 80-120 entries selected from the dataset as complete family-shaped slices,
not isolated popular Digimon. Include a small number of Baby/In-Training forms, broad
Rookie choices, and complete paths through Mega where the source supports them. Put
release selection, encounter tier, story role, and scan cost in the PMDO overlay.

Each story role receives a deliberate replacement. Never select an NPC automatically
by body shape or alphabetical proximity. Use semantic actor IDs such as `shop_owner`
in scripts and resolve them through one cast table.

### Stable identity

Use lowercase stable IDs derived by the importer, such as `agumon`, and never reuse a
retired ID. Preserve the Kaggle display name separately. Each production entry needs:

* stage, type, attribute, memory/equipment values, and source stats;
* source learnset and skill definitions;
* incoming and outgoing digivolutions and their source requirements;
* PMDO growth, combat conversion, release state, encounter and scan settings;
* one static 2D image and its rights/provenance through Phase 3; and
* localization and explicit attribution.

### Digivolution graph

The existing `PromoteFrom` plus `Promotions` model has a preferred parent and cannot
faithfully represent Digimon's many-to-many graph. Add a runtime-owned transition edge:

```text
from, to, direction, requirements[], costs[], priority, discovered
```

Import source edges and requirements from the Kaggle tables. Translate supported
requirements into composable runtime conditions (level, stats, ABI-like progression,
CAM-like bond, item, DigiCode, or story flag) in the overlay rather than hard-coding
species. Each forward edge also exposes its valid reverse destination. Every released
non-root form must have a dedigivolution route; branch selection must be explicit when
more than one destination is possible.

Store identity independently from current form: nickname, personality, bond, unlocked
skills, discovered branches, and highest stage survive both directions. Recalculate
form stats deterministically, preserve HP percentage, validate skill/equipment state,
and make the entire transition transactional so a failure consumes nothing.

### Scan Data acquisition

Add a new-save ledger keyed by species ID:

```text
scan_points, code_unlocked, first_source, unlock_count, variants_discovered
```

After a hostile Digimon's confirmed defeat, award scans once per unique spawned entity
before it is discarded. Summons, illusions, friendly or neutral actors, PvP ghosts,
and scripted defeats yield nothing unless explicitly enabled. Globally disable
`JoinRate` and every direct/random join path.

Initial tuning should be transparent and data-driven:

* ordinary eligible defeats grant 25 points, adjusted by stage and dungeon;
* a common DigiCode requires 100 points (about four comparable encounters);
* important rare lines receive a guaranteed quest or boss source;
* ordinary gains are capped per species per floor to prevent summon farming;
* excess scans become Bits or branch materials; and
* unlocked allies are instantiated only at a hub terminal after roster confirmation.

Always show immediate progress, for example `Agumon Scan Data 50/100`. This delivers
the defeated-opponent requirement without hiding recruitment behind another random
roll.

## Implementation plan

### Phase 0 — baseline and guardrails

1. Restore the pinned submodules and build the untouched game.
2. Inventory creature references across C#, generated assets, Lua, maps, dialogue,
   localization, and visuals.
3. Add a validator for forbidden Pokemon, dangling IDs, invalid graphs, missing static
   images/localization, and accidental recruitability.
4. Pin the Kaggle download checksum and normalize all five tables with the importer.

**Gate:** baseline build succeeds; importer tests pass; the audit identifies every
Pokemon reference and fails when a broken edge or Pokemon NPC is deliberately added.

### Phase 1 — playable vertical slice

1. Start with one source-supported line each for Agumon, Gabumon, Biyomon,
   Tentomon, Palmon, Gomamon, Patamon, and Gatomon. These eight selected lines
   contain 44 unique forms and are recorded in `DataAsset/Digimon/phase1_roster.json`.
   Author the PMDO overlay for stats, skills, requirements, and scan thresholds next.
   Alternative branches are deferred by the user's initial single-line decision;
   retain the full source graph for later expansion.
2. Implement persistent graph digivolution/dedigivolution and identity preservation in
   PMDC/RogueEssence, including requirement previews and transactional state changes.
3. Replace recruitment with the Scan Data ledger, post-defeat award service, result UI,
   and hub restoration terminal.
4. Add the static-image creature renderer used whenever an animation is unavailable.
5. Convert one town, every NPC in it, one dungeon, its boss, dialogue, items, encounters,
   and starter/partner choices. Images must be original or properly licensed.
6. Add a new-save format version; no migration code or compatibility alias table.

**Gate:** from a fresh save, every visible creature is a Digimon; the player can defeat,
scan, restore, recruit, digivolve along each selected line, dedigivolve, save/reload,
and finish the dungeon using static images with no missing references.

**Current implementation status (2026-09-10):** the 44-form runtime slice is
implemented: source-derived level curves, 115 adapted skills, 80 permanent graph
transitions, retained identity, repeated dedigivolution training, confirmed-defeat
Scan Data, restoration into reserves, signpost menus, static sprites/portraits,
eight starting choices, deterministic Champion-or-lower hub NPCs, and scoped
early-stage Tropical Path encounters. Dialogue and item conversion are deferred by
user instruction. The final regular floor has a Koromon guardian. The secret room
is retained, and both completion routes return to Base Camp.

The first published build was played by the user. Their secret-room crash exposed
a removed segment still referenced by stairs; that exporter bug is repaired and
covered with seeded native map-generation checks. The corrected boss/exit flow
still needs a complete interactive playthrough. Tests cover graph changes,
rollback, training, scan deduplication, restoration, native record loading and
character save serialization. Source skill secondary effects/penetration remain
explicit combat approximations, recorded in `phase1_skill_adaptations.json`.
Image scaling and white backgrounds are accepted for now and tracked for Phase 4.

### Phase 2 — systems and full roster

1. Add curated entries family by family, then convert techniques, traits, consumables,
   equipment, economy, crafting, rewards, and shops.
2. Convert every generated and scripted encounter plus every NPC via the cast table.
3. Rewrite tutorials and vocabulary around the Digital World, Digivolution, Analyzer,
   Scan Data, DigiCodes, and Bits instead of doing a blind word replacement.
4. Balance stage curves, scans, requirements, enemy AI, and dungeon depth with seeded
   simulation telemetry.

**Gate:** every released entry has valid source data, overlay, line, skill set, static
image, habitat or special source, and acquisition route; no Pokemon reference remains.

### Phase 3 — full campaign and polish

1. Rewrite and replay every mission, cutscene, town, dungeon, boss, and postgame event.
2. Convert title, UI, field guide, map decoration, icons, credits, wiki, deployment, and
   localization outputs. Audio remains unchanged and outside conversion acceptance.
3. Prove each required DigiCode, item, flag, and terminal is available before use for
   every starter choice, including loss/retry and full-roster cases.
4. Run controller/keyboard UI, performance, accessibility, localization, attribution,
   and clean-save campaign reviews.

**Gate:** complete fresh-save playthroughs pass and all shipped new visuals have
documented permission and provenance.

### Phase 4 — visual production

User playtest follow-up (2026-09-10): replace white backgrounds with proper
transparency and improve downsampling/render size so Digimon remain legible. Keep
original source images intact and prepare separate runtime art. These changes
are deferred from Phase 1.


Replace static stand-ins with complete sprite sheets, portraits, directional movement,
combat reactions, effects, and polished digital UI transitions. Visual upgrades must
not change creature IDs, graph behavior, or save state. There is no temporary battle
digivolution or audio work in this phase.

## Validation matrix

Run these checks against both source and generated output:

| Area | Required checks |
| --- | --- |
| Dataset | All five named CSVs load; stable IDs are unique; skill/species references resolve; output is deterministic; source version/checksum is recorded. |
| Identity | Every player, NPC, speaker, spawn, boss, target, portrait/image, and scripted actor resolves to a released Digimon. |
| Transitions | Targets exist; requirements can be met; every non-root form dedigivolves; explicit branch choice is deterministic; preview equals result. |
| State | Nickname, personality, bond, skills, discoveries, equipment, and HP policy survive both transitions and save/load; failures consume nothing. |
| Acquisition | Only eligible confirmed defeats award once; excluded/summoned actors award zero; no direct join path remains; progress and caps are correct. |
| Progression | Every required scan, item, flag, terminal, and opponent is reachable before use; no starter can deadlock the campaign. |
| Presentation | Static fallback images fit dungeon, dialogue, party, result, and terminal views through Phase 3; missing images fail validation. |
| Content | All IDs, localization, skills, items, roles, encounters, credits, and references exist; Pokemon-reference audit is empty. |

Manual coverage includes every starter/partner pair, story boss, shop/service actor,
branch-choice screen, full party/roster, simultaneous defeat and scan, save/reload in
each form, and credits.

## Additional Digimon identity

Recommended after the core loop is stable:

1. **DigiFarm/server:** reserves produce capped training affinity or research.
2. **Analyzer field guide:** progressively reveal silhouettes, scans, techniques,
   attributes, habitats, and discovered branches.
3. **Vaccine/Data/Virus triangle:** add a modest secondary modifier (start near 10-15%)
   without replacing PMDO's elemental combat.
4. **Meaningful branching:** visible bond, stats, training, quest, and plugin conditions
   make line choice deliberate rather than opaque.
5. **Digital biomes:** packet storms, firewalls, broken sectors, compression traps,
   data currents, terminals, and corruption fields adapt existing dungeon mechanics.
6. **Technique inheritance:** retain a limited mastered pool through dedigivolution so
   branching matters without enabling unrestricted best-skill stacking.
7. **Care and bond:** food, rest, missions, and dialogue affect bond and branch access,
   but never create irreversible failure from hidden care mistakes.
8. **Jogress expeditions:** compatible allies combine through an explicit persistent
   graph transition with clear identity/skill rules; this is not a timed battle form.
9. **Digital presentation:** terminal layouts, readable glitch effects, restrained
   scanlines, packet-transfer results, and evolving field-guide entries establish tone.

## Principal risks

* **Unavailable engine/assets:** restore and pin submodules before claiming the vertical
  slice is complete.
* **Dataset mismatch:** retain source rows, pin checksums, validate references, and put
  PMDO interpretations in a separate overlay.
* **Many-to-many lines:** use one versioned graph service, never `PromoteFrom` special
  cases distributed across species.
* **Hidden Pokemon:** audit generated output and traverse runtime maps/scripts, not just
  source text.
* **Scan grind:** display progress, guarantee rare sources, tune per species, and measure
  time-to-code in seeded runs.
* **Static-image readability:** provide clear facing/selection/condition markers and
  test every UI context before animation production.
* **Rights:** confirm rights for the Digimon property, Kaggle dataset, and every visual;
  keep attribution and provenance with release artifacts.

## Immediate backlog

1. Convert the selected skills into executable runtime mappings; stat/progression
   balance is now authored separately and validated, pending playtest tuning.
2. Choose the town/dungeon/boss and deliberate NPC cast using the selected forms.
3. Implement graph transitions, identity preservation, Scan Data and restoration,
   static presentation, and fresh-save contracts in the actual runtime.
4. Integrate the supplied source images into all required rendering/UI contexts.
5. Convert the one-town/one-dungeon slice and pass the updated single-line Phase 1 gate.
6. Resolve source skill variants before releasing any additional affected species;
   establish visual redistribution provenance before release.

Do not mass-produce images or rewrite the full campaign before the transition,
acquisition, validation, static-rendering, and new-save contracts pass the slice.

## Confirmed scope and full-roster rules (2026-09-10)

Phase 1 changes are limited to Tropical Path (including its own secret room) and
Base Camp/Town. Dialogue rewriting and item conversion are deferred. Completion
returns to Base Camp. Shared runtime code supplies Digimon behavior without
converting other maps.

For Phase 2, the five NX forms retain the source no-evolution rule and use
restoration acquisition. Remove Cyber Sleuth story-completion requirements for now.
Keep item and fusion unlocks. Prefer fusion with both required Digimon present in
the active party. If that cannot be implemented reliably, the approved fallback
is an item awarded when one partner reaches the required level, held by the other
partner to satisfy the fusion requirement. Fusion consumption and identity rules
will be documented with the implementation.
