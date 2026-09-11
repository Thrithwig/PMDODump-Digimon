# Digivolution stat retention

Retention is 20%, rounded down separately on each transition. Fractions are discarded, not banked.

Both digivolution and dedigivolution reset level to 1 and EXP to 0.
For each stat, the new permanent bonus is:

`previously retained + floor((current-form level growth + new training) / 5)`

Level growth uses that form's actual stat curve, from its cycle starting level
(the scan-restored level for a newly restored Digimon) to its current level.
Base stats, equipment and temporary battle modifiers do not count as gains.
New training is the current bonus minus the previously retained amount.
The existing 256-per-stat bonus cap remains. Source SP follows the same rule.
Immediate form changes without leveling or training add no bonuses.
Existing retained bonuses are not reduced to twenty percent again on later changes.

The Stats summary adds a Retained column after a successful form change. These
values are already included in the displayed totals and in Boosts. The column
persists through character serialization, and is visible in either summary view.

Older saves did not record the split between training and retained bonuses.
Their current bonus is treated as unclassified training on the next transition;
old evolution history cannot be reconstructed retroactively. Future transitions
record the split explicitly. The older flat dedigivolution bonus is superseded.

Tests cover both directions, level and EXP reset, training, immediate toggles,
failed-transition rollback and save serialization. Native checks use actual
Digimon stat curves and engine Character objects.
