# PMDO move mechanics reference

This is a source-backed menu for the Digimon move generator.  Reuse these
serializable PMDO/RogueEssence types; do not add a parallel targeting system.
The canonical construction examples are in
`DataGenerator/Data/Skills/SkillsPMD.cs`; dumped JSON in `DumpAsset/Data/Skill`
shows the exact persisted envelope.

## Source layer and baseline envelope

`DataAsset/Digimon/Source/Skills.csv` is the input list, but the current
Digimon dump files are generated data.  A redesign generator should emit the
same `SkillData` shape as `DumpAsset/Data/Skill/*.json`, with this invariant
for ordinary damaging moves:

```json
"Data": {
  "Element": "water", "Category": 1, "HitRate": 95,
  "SkillStates": [{ "$type": "RogueEssence.Dungeon.BasePowerState, RogueEssence", "Power": 35 }],
  "OnHits": [{ "Key": { "str": [-1] }, "Value": { "$type": "PMDC.Dungeon.DamageFormulaEvent, PMDC" } }],
  "BeforeTryActions": [], "BeforeActions": [], "OnActions": [],
  "BeforeExplosions": [], "BeforeHits": [], "OnHitTiles": [],
  "AfterActions": [], "ElementEffects": []
}
```

`Category` is `1` Physical, `2` Magical/Special, `3` Status.  Category does
not constrain the action type.  `BaseCharges` is PP; enforce `<= 30`.  Keep
the normal damage event at `OnHits[-1]`; use priority `0` for a secondary
effect.  `Strikes` controls fixed repeated hits.

All actions also have `TargetAlignments`, `TileEmitter`, `PreActions`,
`ActionFX`, and `LagBehindTime`; preserve the dumper's defaults if visuals are
not intentionally redesigned.  `Alignment.Foe` serializes as `4`; dangerous
ally-hitting attacks use `Alignment.Friend | Alignment.Foe` (serializes as
`6`) on **both** `HitboxAction.TargetAlignments` and
`Explosion.TargetAlignments`.

## Action recipes

| Tactical shape | Reusable action and required fields | Native representatives |
|---|---|---|
| Adjacent single target | `AttackAction`; `WideAngle: 0` (Front), foe alignment | `ice_hammer`, `close_combat` |
| Adjacent sweep | `AttackAction`; `WideAngle` `Wide`, `FrontAndCorners`, or `Around` | action implementation in `CharAction.cs`; use for claws/tails, not a projectile |
| Ranged shot / beam | `ProjectileAction`; `Range`, `Speed`, `StopAtHit`, `StopAtWall`, `HitTiles`; `StopAtHit: false` pierces | `ice_beam`, `acid`, `poison_sting` |
| Multi-ray projectile | `ProjectileAction` plus `Rays` (`Three` is used by Pin Missile) and `Strikes` | `pin_missile` |
| Dash / lunge | `DashAction`; `Range`, `StopAtHit`, `StopAtWall`, `HitTiles`, optional `WideAngle`, `SnapBack`, `AppearanceMod` | `wing_attack`, `double_edge`, `twineedle` |
| Cone | `AreaAction`; `HitArea: Cone`, `Range`, `Speed` | `ember`, `tail_whip`, `mega_drain` |
| User-centered blast | `AreaAction`; `HitArea: Full`, `Range`, `Speed`; choose foe-only or friend+foe alignment explicitly | `earthquake`, `whirlwind` |
| Directional offset blast | `OffsetAction`; `Range` is landing distance and `HitArea` is `Tile`, `Sides`, `Cross`, or `Area` | `CharAction.cs` `OffsetAction`; suitable for an impact detonation |
| Thrown arc | `ThrowAction`; `Coverage`, `Range`, `Speed`, `Anim` | `leech_seed` |
| Wave / broad line | `WaveMotionAction` (a `LinearAction`); inspect a native JSON instance before generator emission | implementation in `CharAction.cs` |
| Room-wide attack | No `RoomAction` exists in `CharAction.cs`.  Use an existing room-targeting battle event only after copying a native use case; do not approximate a room effect with an enormous `AreaAction`. |

For projectile and dash, `StopAtHit: true` produces the usual first-target
behavior.  A piercing beam must set `StopAtHit: false`; `StopAtWall` remains
the wall boundary.  `Range` is in tiles.  `AreaAction` supports `Full`,
`Cone`, `Cross`, and `Sides`.  `AttackAction` is an adjacent pattern; it is
valid for Special Lightning Claw / Lightning Paw-style skills.

## Effect recipes and event ordering

### Guaranteed damage plus a stat stage change

Put `DamageFormulaEvent` first at priority `-1`, then a target stat event at
priority `0`:

```json
{ "Key": {"str": [0]}, "Value": {
  "$type": "PMDC.Dungeon.StatusStackBattleEvent, PMDC",
  "Stack": -1, "StatusID": "mod_defense",
  "AffectTarget": true, "SelfInflicted": false,
  "SilentCheck": true, "Anonymous": false, "TriggerMsg": {"Key": null}, "Anims": []
}}
```

The supported stage IDs are `mod_attack`, `mod_defense`,
`mod_special_attack`, `mod_special_defense`, `mod_speed`, `mod_accuracy`, and
`mod_evasion`.  Status data clamps these to -6..+6.  Use an explicit
`StatusStackBattleEvent` for guaranteed effects; do not wrap it in an
additional-effect event.

### Chance-based status or debuff

The flag and the wrapper must appear together:

```json
"SkillStates": [
  {"$type":"RogueEssence.Dungeon.BasePowerState, RogueEssence","Power":35},
  {"$type":"PMDC.Dungeon.AdditionalEffectState, PMDC","EffectChance":25}
],
"OnHits": [
  {"Key":{"str":[-1]},"Value":{"$type":"PMDC.Dungeon.DamageFormulaEvent, PMDC"}},
  {"Key":{"str":[0]},"Value":{
    "$type":"PMDC.Dungeon.AdditionalEvent, PMDC", "BaseEvents":[
      {"$type":"PMDC.Dungeon.StatusBattleEvent, PMDC","StatusID":"paralyze",
       "AffectTarget":true,"SelfInflicted":false,"SilentCheck":true,"Anonymous":false,
       "TriggerMsg":{"Key":null},"Anims":[]}
    ]
  }}
]
```

`AdditionalEvent` only runs after **damage was dealt** and rolls
`AdditionalEffectState.EffectChance`; it selects one event if several are in
`BaseEvents`.  It belongs in `OnHits`, not `AfterActions`.  Native examples:
`ice_beam` (freeze), `acid` (Sp. Def down), `poison_sting` (poison).

For guaranteed status use `StatusBattleEvent` directly at priority `0`.
Useful established status IDs include `burn`, `freeze`, `paralyze`, `poison`,
`poison_toxic`, `sleep`, `confuse`, `flinch`, and `immobilized`.

### Knockback, drain, recoil, multi-hit, and positive effects

* Knockback: `OnHits[0] = KnockBackEvent(Distance)`.  Native `strength` uses
  `OnHitEvent(..., new KnockBackEvent(1))`; `whirlwind` uses `KnockBackEvent(8)`.
  Knockback respects `AnchorState` and stops against dungeon constraints.
* Drain: `AfterActions[0] = HPDrainEvent(Fraction)` after normal damage, and
  add `HealState`.  Native `absorb` / `mega_drain` use fraction `2`.
* Recoil: `AfterActions[0] = HPRecoilEvent(Fraction, true)` for max-HP recoil
  or `DamageRecoilEvent(Fraction)` for damage-derived recoil.  The recoil code
  runs only if total damage was dealt.  Native `double_edge` uses `5`.
* Multi-hit: set `Strikes` (for example 2 for Twineedle, 4 for Pin Missile).
  Lower per-hit power and PP accordingly.
* Positive self effects: place `StatusStackBattleEvent` in `AfterActions` with
  `AffectTarget: false`, `SelfInflicted: true`; `AdditionalEndEvent` is the
  chance-gated aggregate-damage variant for after-action effects.

## Terrain and tile effects

Tile effects require an action with `HitTiles: true`, then add an event to
`OnHitTiles`.  The existing generator reuses
`RemoveTerrainStateEvent` with `FoliageTerrainState`, `WallTerrainState`,
`WaterTerrainState`, `LavaTerrainState`, and/or `AbyssTerrainState`; it also
uses `ShatterTerrainEvent("wall")`.  Copy a native construction from
`SkillsPMD.cs` rather than hard-code guessed JSON for emitters/`FlagType`.
Reserve terrain removal for named moves that plausibly cut, shatter, melt, or
clear terrain.

## Implementation cautions

1. Set hitbox and explosion alignments together.  Forgetting `Explosion` is a
   common way to make an otherwise dangerous AOE accidentally ally-safe.
2. Do not add `AdditionalEffectState` without `AdditionalEvent`, or vice versa:
   the state alone has no effect and `AdditionalEvent` otherwise reads the
   default chance.
3. Preserve event order: damage `-1`; per-target consequences `0`;
   aggregate drain/recoil/self effects in `AfterActions`.  Use
   `AdditionalEndEvent`, not `AdditionalEvent`, when the effect depends on
   total damage across an AOE/multihit action.
4. `AreaAction` is centered on the user; use `OffsetAction` for a detonation
   in front of the user.  Do not use a user-centered `AreaAction` to fake a
   forward blast.
5. Physical versus Special is only `Data.Category`; all geometry recipes can
   be used by either.  Convert Ice Archery I/II/III to `ProjectileAction` as
   physical ranged attacks.  Keep Lightning Claw/Paw-style entries special
   while assigning `AttackAction` for close range.
6. The current Digimon dumps contain PP values above the requested cap (for
   example `digi_rare_metal_poop` 38 and `digi_awesome_quake_i` 39), so PP must
   be normalized at the source/generator layer and regenerated.

## Most useful template paths

* `DataGenerator/Data/Skills/SkillsPMD.cs`: all production construction
  patterns, notably Wing Attack (dash), Ember (cone), Strength (knockback),
  Absorb (drain), Double-Edge (recoil), Pin Missile (rays + strikes), Acid
  (chance stat drop), and Whirlwind (friendly-fire area knockback).
* `DumpAsset/Data/Skill/ice_beam.json`: exact serialized ranged Special plus
  chance status envelope.
* `DumpAsset/Data/Skill/close_combat.json`: exact `AfterActions` self-debuff
  envelope.
* `PMDC/RogueEssence/RogueEssence/Dungeon/Characters/CharAction.cs`: action
  field semantics.
* `PMDC/PMDC/Dungeon/GameEffects/SkillState.cs`,
  `BattleEvent/ConditionalBattleEvent.cs`, `BattleEvent/DisplaceBattleEvent.cs`,
  and `BattleEvent/RecoilBattleEvent.cs`: chance, event, displacement, and
  recoil semantics.
