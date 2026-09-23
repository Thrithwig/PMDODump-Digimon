# Cyber Sleuth damage matchups

The conversion keeps PMDO's base damage formula, criticals, explicit item and
ability effects, and fixed-damage behavior. It replaces the Pokemon matchup
chart and removes the automatic same-element attack bonus for Digimon.

Cyber Sleuth's type advantage is reduced from 2x to **1.5x** by owner request.
The unfavorable type direction remains **0.5x**. Same types, Free, and missing
type data are neutral. The cycle is **Virus > Data > Vaccine > Virus**.
The native form's `DigimonAttribute` supplies this classification, so evolution
and devolution immediately use the new form. It is independent of element and
`Family_Types`.

Element uses the attack's element and the defender's current element:

- Fire > Plant > Water > Fire.
- Electric > Wind > Earth > Electric.
- Light > Dark and Dark > Light.

These eight pairings give **1.5x**. Every other pairing is neutral, including
Wind against Plant, matching elements, Neutral, and unused legacy elements.
There are no automatic elemental resistances or immunities. Explicit ability
and treasure effects still apply through PMDO's existing event system.

Type and elemental modifiers multiply before the normal integer damage
calculation: both favorable = 2.25x; unfavorable type plus favorable element =
0.75x. Other modifiers and normal damage rounding can affect displayed HP loss.
Fixed-damage moves keep their stated damage rather than gaining these bonuses.

The supplied IGN page could not be retrieved. The source rules were checked
against the [official Cyber Sleuth: Hacker's Memory manual, Battle page 30](https://d1vtv52f4vjbmu.cloudfront.net/manuals/digimon-story-hacker-memory/108_18_OnlineManual_Digimon_Cyber_Sleuth_Hacker%27s_Memory_PS4_GB_QS.pdf).

## Rebuild

`DigimonMatchups.ConfigureElements` is shared by the full universal-data
generator and the scoped update command. To update an existing conversion
without replacing its other universal settings:

```text
dotnet build PMDOData.sln --no-restore
cd DataGenerator/bin/Debug/net8.0
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-matchups
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-check
```

Native checks cover every type pair and every stored element pair, combined
physical/magical modifiers, Free/missing data, and Wind against Plant.
