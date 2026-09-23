# Final move redesign audit

Audited the installed `DumpAsset/Data/Skill/digi_*.json` catalog together with
the 506-source-skill manifest, reviewed designs, access records, compiler, and
`after.json`. This is a structural and data-semantics audit. It does not claim
that a full dungeon scene executed every hitbox or battle event.

## Coverage and identity

- Installed definitions: **522** = **506** source skills plus **16** starters.
- The 506 manifest IDs and reviewed design IDs match exactly; all are present in
  the 522 installed definitions.
- Source comments and element mappings matched all 506 installed source skills.
- Category mapping matched source type: 297 Physical, 170 Special, and 55
  Support in the installed catalog. Lightning Paw is Special/AttackAction; all
  three Ice Archery moves are Physical/ProjectileAction.

## Catalog shape and balance summary

- PP is 8–29 (median 20, mean 19.37). Power is 10–65 (median 35, mean
  35.42); total multi-hit power is 20–65 (median 38, mean 38.61). This
  includes the repaired Revenge Flame, bringing the damaging-move count to
  467.
- Geometry is varied: 122 close, 112 ranged, 64 area, 50 thrown, 46 beam,
  42 dash, 23 cone, 20 offset, 13 self, 14 wave, and 16 sweep actions.
- 38 moves deliberately permit friendly fire. The installed hitbox and
  explosion masks agree for every generated definition.
- Shared single-hit generic moves now remain at or below the highest-stage
  55-power guide; the audit found no violation. `saint_knuckle_iii` is now
  50 power at its 47.56 access center. The only 65-power entries are
  Mega-exclusive tier-III moves: `gale_storm_iii`, `ocean_wave_iii`,
  `rune_forest_iii`, and `thunder_fall_iii` (all 14 PP). These remain normal
  playtest watch items rather than release-blocking defects.

## Native semantics checked

Every installed definition was checked for valid PP, released state, element,
status reference, action and explosion envelope, and serialization round trip
by the runtime check. The audit also inspected compiler construction:

- chance effects use `AdditionalEffectState` with an additional-event wrapper;
  guaranteed target stat changes use hit-gated native events;
- knockback, drain, recoil, terrain, fixed damage, and multi-hit entries are
  emitted through existing PMDO event classes, not custom event data;
- the 668 move IDs accepted by specific-skill passives were checked against the
  installed category/power/accuracy data. All damage-modifier targets now have
  a damage payload, and no accepted accuracy move is guaranteed-hit
  (`HitRate == -1`).

## Resolved findings

The following issues were found in the first audit pass and verified resolved
in regenerated native assets:

| Move | Installed action | Verified correction |
|---|---|---|
| `revenge_flame` | AttackAction, Magical, power 25, PP 12 | Restored a `DamageFormulaEvent` for MetalGreymon Blue's damage anchor and adds Counter plus Mirror Coat as after-action self effects. |
| `strike_of_the_seven_stars` | OffsetAction, range 3, 3×3, 3 strikes | The friendly-fire seven-star attack now has an actual offset-area hitbox, rather than a first-contact projectile. |
| `transcendent_sword__omnimon` | AttackAction, `WideAngle: 2` | Replaced the first-contact dash with a three-tile forward friendly-fire sweep. |
| `transcendent_sword__omnimon_nx` | AttackAction, `WideAngle: 2` | Same three-tile sweep correction as the standard form. |

These regenerated assets have matching hitbox and explosion alignment masks.
No remaining specific structural, shared-access balance, or
passive-compatibility failure was found in the final recheck. The four
Mega-exclusive 65-power tier-III entries remain a playtest watch-list rather
than a release-blocking defect.
