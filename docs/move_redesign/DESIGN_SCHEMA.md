# Move redesign authoring contract

The three batch JSON files under `DataAsset/Digimon/MoveRedesign/designs` are
the reviewed move source. They contain `{ "moves": [ ... ] }`, one record per
assigned source skill ID. Never change IDs, source category/element, or learnsets.
Read your input subset, access audit, and MECHANICS.md. Do not read all other batches.

Required fields for each record:

* `id`: bare source skill ID, without `digi_`.
* `power`: positive integer per hit, or null for Support. Fixed uses fixed damage.
* `pp`: 1..30, catalog median near 20. Most routine moves 20..26, strong area,
  status, multihit moves usually 12..18. Avoid systematically starving signatures.
* `accuracy`: 1..100, or -1 for deliberate never-miss attacks; ordinary damage
  normally 85..100. Standalone status moves may use lower hit rates.
* `template`: an existing native skill ID from templates.json, for graphics and
  matching native action class. All damage/effect logic will be cleared and rebuilt.
* `shape`: melee, sweep, projectile, beam, dash, cone, burst, offset, throw, wave,
  self, or native. `native` is only for Support: preserve template effects/geometry.
* `range`: melee/sweep/self=1; shots 2..8, dash 2..4, cone/burst 1..3,
  offset 2..4, throw 2..5, wave 3..6. Never simulate room targeting with huge ranges.
* `targets`: foes, all, allies, self, or party. Damage uses foes or all (friend+foe).
* `strikes`: 1 normally, 2..3 for thematic multi-hit; total power is per-hit times
  strikes. Account for multiple status rolls; do not attach strong procs to multihits.
* `effects`: [] or list from the vocabulary below. One secondary effect normally;
  at most two for a signature, simple generic skills normally zero or one.
* `reason`: concrete theme, access, and balancing explanation, not a template phrase.

Optional `hit_fx_template` overrides only native impact visuals for close Special
attacks, etc. Optional `exception` explains deliberate starter/low-power/outlier
behavior. Category and element come directly from the manifest, not this design.

Effects (no arbitrary engine JSON in design files):

* `{ "kind":"stat", "stat":"mod_defense", "stages":-1,
  "target":"foe", "chance":25 }`: target can also be self. Valid stat IDs:
  mod_attack, mod_defense, mod_special_attack, mod_special_defense, mod_speed,
  mod_accuracy, mod_evasion. One stage generally; rare two-stage moves pay in power/PP.
* `{ "kind":"status", "status":"paralyze", "target":"foe", "chance":20 }`.
  Use native IDs burn, freeze, paralyze, poison, poison_toxic, sleep, confuse,
  flinch, immobilized. Strong disable chances normally <=20%, multihit <=10%.
* `{ "kind":"knockback", "distance":1 }`: successful damaging hit only.
* `{ "kind":"drain", "fraction":4 }`: heal one quarter of total damage.
* `{ "kind":"recoil", "fraction":4 }`: lose one quarter of damage dealt.
* `{ "kind":"critical", "stages":1 }`: native critical boost for this attack.
* `{ "kind":"terrain", "terrain":"foliage" }`: native tile removal. Only
  foliage or wall; wall-breaking signatures exceptional and low PP.
* `{ "kind":"heal", "numerator":1, "denominator":4 }`: support restores target HP.
* `{ "kind":"revive" }`: native dungeon party revival; self targeting only.
* `{ "kind":"cure", "statuses":["poison", "poison_toxic"] }`: support cure.
* `{ "kind":"cleanse", "group":"ailments" }`: cure bad status conditions;
  group `negative` instead removes only negative stat changes.

Effect target `target` is also accepted for beneficial effects on allied targets.
Source `Direct` skills that have no damaging component can use null power to
adapt to native Status category. The source Direct label remains in the manifest.
Native support templates must be released and contain actual effect events.

Chance 100 is guaranteed. Only one non-100 proc chance per move (the native
AdditionalEffectState is shared). Do not use chance on drain/recoil/critical/terrain.
For custom support effects, use a matching geometry template and shape (not native).
Support `native` may use no extra effects; compiler keeps its verified PMDO effects.
Its description is derived from the template, so choose one whose behavior fits.

Balance around access.stagePowerCenter.weightedTarget (25/35/45/55 stage guides),
then trade raw damage against reach, area, movement, accuracy, effects, ally risk,
and PP. Shared skills use intermediate access centers, never highest stage alone.
Baby/In-Training starting skills may be 20; added 14 starters remain unchanged.
Generic I/II/III progressions should increase damage/utility with sensible PP cost.
Physical need not be melee; Special need not be ranged. Lightning Paw must stay
Special, melee. Ice Archery I/II/III must be ranged Physical.

Choose each signature's geometry/effect by fantasy; avoid implementing the entire
batch with name substring rules. Automation may populate routine numerical values,
but inspect the resulting moves and explicitly design thematic exceptions.
