# Digimon family items

Design matrix for the family-exclusive items. Source of truth: `DataAsset/Digimon/family_items.json`;
families come from `docs/DIGIMON_FAMILY_TYPES.md`. Items are generated with
`DataGenerator -digimon-items` and reuse PMDO exclusive-item effects; no new battle code.

## How it works

- **Eligibility.** Each item carries the family's member species in PMDO's `FamilyState`, filled from the
  installed Digimon forms. Because the check is against the holder's current species, digivolving into or
  out of a family updates eligibility with no extra code. A Digimon in several families can use any of them;
  one held item at a time means effects never stack.
- **Drops.** ★ items are rarity 1 and ★★ items rarity 2. Treasure boxes roll from the species-to-rarity map
  using the species present on that floor, so a box near Reptiles holds Reptile treasures. Light boxes use
  rarity 1, deep boxes rarity 2. ★★★ items are rarity 3 and never drop.
- **Exchange.** ★★★ items come from the Base Camp swap shop for the family's first ★ and first ★★ item.
  Recipes are generated into `origin/digimon/family_trades.lua`.
- **Names.** Player-facing text says Digimon and uses Digimon element names (Light for fairy, Plant for
  grass, Earth for ground, Wind for flying, Neutral for normal).

## Rebuild

```text
python Scripts/digimon_family_items.py
dotnet build PMDOData.sln --no-restore
cd DataGenerator/bin/Debug/net8.0
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-items ../../../../DataAsset/Digimon/family_items.json
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -index Item
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-check
```

The first command validates the design and rewrites this file. The item index step also rebuilds the
species-to-rarity map in `Data/Misc/Rarity.json` that treasure boxes read.

33 families, 132 items.

## Matrix

### Cyborg (36 members)

*Armoured augmentations on Electric and Fire bodies; balanced and durable, the biggest family.* Representative: Andromon, Boltmon, CannonBeemon, Cyberdramon, Darkdramon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Surge Guard | the Digimon becomes immune to the Paralyzed status. | `StatusImmune` | treasure box (rarity 1) |
| ★ | Optic Sight | the Digimon's moves and items that hit in a straight line cannot damage allies. | `GapProber` | treasure box (rarity 1) |
| ★★ | Grounding Spike | it reduces damage done by Earth-type attacks. | `WeaknessReduce` | deep treasure box (rarity 2) |
| ★★ | Reactive Armor | the Digimon scatters Spikes when hit by a Physical attack. | `SpikeDropper` | deep treasure box (rarity 2) |
| ★★★ | Full Burst Array | the Digimon's regular attack explodes outwards with splash damage. | `ExplosiveAttack` | swap shop |

Exchange: Full Burst Array for Surge Guard + Grounding Spike.

### Dragon (33 members)

*Fire-breathing bruisers with the highest HP and Attack; slow to hit, brutal when they do.* Representative: AeroVeedramon, Breakdramon, BurningGreymon, Coredramon (Blue), Coredramon (Green) ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Ember Whisker | it raises the critical-hit ratio of not-very-effective hits. | `NVECrit` | treasure box (rarity 1) |
| ★ | Drake Claw | the Digimon will do increased damage if its previous move missed. | `PracticeSwinger` | treasure box (rarity 1) |
| ★★ | Wyrm Crest | it raises the critical-hit ratio of super-effective hits. | `SuperCrit` | deep treasure box (rarity 2) |
| ★★ | Furnace Heart | the Digimon's regular attacks and thrown items have a chance to inflict the Burned status. | `StatusOnAttack` | deep treasure box (rarity 2) |
| ★★★ | Rampart Breaker | some of the Digimon's moves will break walls. | `Wallbreaker` | swap shop |

Exchange: Rampart Breaker for Ember Whisker + Wyrm Crest.

### Warrior (26 members)

*Sword and fist fighters; fast physical attackers built around the regular attack.* Representative: Alphamon, Alphamon NX, ChaosGallantmon, Crusadermon, Crusadermon NX ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Resolute Gauntlet | the Digimon cannot have its Attack lowered. | `StatDropImmune` | treasure box (rarity 1) |
| ★ | Iron Greaves | the Digimon is prevented from being forced off its location. | `Anchor` | treasure box (rarity 1) |
| ★★ | Twin Edge | it allows the Digimon's regular attack to strike twice. | `DoubleAttacker` | deep treasure box (rarity 2) |
| ★★ | Blitz Bandana | it changes the Digimon's regular attack into a dash. | `LungeAttack` | deep treasure box (rarity 2) |
| ★★★ | Champion's Standard | the Digimon's attacks never miss and always land a critical hit if all moves have the same PP. | `BetterOdds` | swap shop |

Exchange: Champion's Standard for Resolute Gauntlet + Twin Edge.

### Holy Warrior (23 members)

*Royal Knights and their kin; Light-aligned, strong in every stat, protectors of the party.* Representative: Alphamon, Alphamon NX, Alphamon Ouryuken, Craniamon, Crusadermon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Knight's Oath | the Digimon cannot damage allies with its moves. | `Nontraitor` | treasure box (rarity 1) |
| ★ | Vigil Lantern | it restores the PP of a move when the Digimon reaches a new floor. | `DeepBreather` | treasure box (rarity 1) |
| ★★ | Paladin's Plate | it reduces damage done by Dark-type attacks. | `WeaknessReduce` | deep treasure box (rarity 2) |
| ★★ | Aegis Mantle | the Digimon will step in to take Dark-type attacks for nearby allies. | `TypeBodyguard` | deep treasure box (rarity 2) |
| ★★★ | Grail of Valor | the Digimon will revive a fallen ally when it defeats an opponent. | `AllyReviverBattle` | swap shop |

Exchange: Grail of Valor for Knight's Oath + Paladin's Plate.

### Android (23 members)

*Electric machines with the best Defense in the game; they hold ground and shoot.* Representative: Andromon, Boltmon, CannonBeemon, Gigadramon, HiAndromon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Alloy Casing | the Digimon cannot have its Defense lowered. | `StatDropImmune` | treasure box (rarity 1) |
| ★ | Coolant Line | the Digimon recovers faster from status problems. | `SelfCurer` | treasure box (rarity 1) |
| ★★ | Gyro Stabilizer | the Digimon will take reduced damage from explosions and splash damage. | `ExplosionGuard` | deep treasure box (rarity 2) |
| ★★ | Pulse Emitter | it allows Electric-type moves to hit Earth-type Digimon. | `TypeBulldozer` | deep treasure box (rarity 2) |
| ★★★ | Bastion Frame | the Digimon will counter damage from regular attacks and thrown items. | `CounterBasher` | swap shop |

Exchange: Bastion Frame for Alloy Casing + Gyro Stabilizer.

### Animal (18 members)

*Earthy scouts and hunters; fragile but quick, at home reading the dungeon.* Representative: Chuumon, Dorugamon, DoruGreymon, Dorumon, Gargomon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Keen Nose | it reveals the number of items laying on the ground whenever the Digimon reaches a new floor. | `AcuteSniffer` | treasure box (rarity 1) |
| ★ | Digging Claws | the Digimon's moves will destroy traps. | `TrapBuster` | treasure box (rarity 1) |
| ★★ | Trail Collar | it reveals the direction of the staircase whenever the Digimon reaches a new floor. | `StairSensor` | deep treasure box (rarity 2) |
| ★★ | Pounce Pads | the Digimon will not take damage from counter attacks. | `HitAndRun` | deep treasure box (rarity 2) |
| ★★★ | Wild Instinct | the Digimon is more likely to evade attacks when at low HP. | `ClutchPerformer` | swap shop |

Exchange: Wild Instinct for Keen Nose + Trail Collar.

### Spiritual Beast (17 members)

*Holy and dark beasts, cats and fox spirits; Dark-leaning special attackers with tricks.* Representative: Antylamon, Arcadiamon Champion, Arcadiamon In-Tr., Arcadiamon Mega, Arcadiamon Rookie ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Moon Bell | the Digimon will be able to move when asleep. | `SleepWalker` | treasure box (rarity 1) |
| ★ | Spirit Charm | the Digimon becomes immune to the Confused status. | `StatusImmune` | treasure box (rarity 1) |
| ★★ | Twilight Veil | status problems inflicted on the Digimon are passed to the Digimon that caused it. | `StatusMirror` | deep treasure box (rarity 2) |
| ★★ | Ninefold Tail | the Digimon's Dark-type moves have a chance to inflict the Confused status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Beckoning Mirror | it warps the attackers away when the Digimon is hit with a Light-type move. | `WarpPayback` | swap shop |

Exchange: Beckoning Mirror for Moon Bell + Twilight Veil.

### Reptile (16 members)

*Agumon, Greymon and the dinosaurs; Fire physical hitters that lead with the jaw.* Representative: Agumon, Agumon (Blk), Ankylomon, BaoHuckmon, Gabumon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Sun Basker | the Digimon recovers HP when in lava. | `HealInLava` | treasure box (rarity 1) |
| ★ | Tail Sweep | the Digimon's regular attack will hit the front and sides. | `WideAttack` | treasure box (rarity 1) |
| ★★ | Nova Tooth | the Digimon's Fire-type moves have a chance to inflict the Burned status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★ | Greymon Helm | the Digimon's regular attack will knock opponents back. | `KnockbackOnAttack` | deep treasure box (rarity 2) |
| ★★★ | Courage Crest | the Digimon's Fire-type moves are boosted. | `SecondSTAB` | swap shop |

Exchange: Courage Crest for Sun Basker + Nova Tooth.

### Beast (15 members)

*Rookie-stage pups and cubs; low stats, so their treasures feed growth and the whole pack.* Representative: Armadillomon, Chuumon, Dorumon, Elecmon, GaoGamon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Foraging Pouch | the Digimon's HP is restored when it eats a food item. | `CheekPouch` | treasure box (rarity 1) |
| ★ | Scent Ribbon | the Digimon will find more \uE024 when exploring in dungeons. | `CoinWatcher` | treasure box (rarity 1) |
| ★★ | Rookie's Pluck | the Digimon gets an extra 3PP to all of its moves. | `PPBoost` | deep treasure box (rarity 2) |
| ★★ | Springy Fur | the Digimon cannot have its Speed lowered. | `StatDropImmune` | deep treasure box (rarity 2) |
| ★★★ | Pack Whistle | the Digimon's stat-changing moves are spread to allies. | `StatusSplash` | swap shop |

Exchange: Pack Whistle for Foraging Pouch + Rookie's Pluck.

### Insectoid (15 members)

*Plant-aligned bugs; armoured, venomous, and good at finding what the dungeon hides.* Representative: CannonBeemon, FanBeemon, GranKuwagamon, HerculesKabuterimon, Hudiemon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Venom Gland | the Digimon becomes immune to the Poisoned status. | `StatusImmune` | treasure box (rarity 1) |
| ★ | Antenna Band | it reveals the number of items laying on the ground whenever the Digimon reaches a new floor. | `AcuteSniffer` | treasure box (rarity 1) |
| ★★ | Stinger | the Digimon's regular attacks and thrown items have a chance to inflict the Poisoned status. | `StatusOnAttack` | deep treasure box (rarity 2) |
| ★★ | Swarm Wings | the Digimon is more likely to evade attacks from far away. | `DistanceDodge` | deep treasure box (rarity 2) |
| ★★★ | Silk Spinner | some of the Digimon's moves will fill water, lava, and pits. | `GapFiller` | swap shop |

Exchange: Silk Spinner for Venom Gland + Stinger.

### Mutant (14 members)

*Oddities like Numemon and Vademon; tough, strange, and unpredictable to fight.* Representative: Apocalymon, CatchMamemon, Dinobeemon, GoldNumemon, Mamemon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Sludge Skin | moves used on the Digimon are more intensely affected by type match-ups. | `ErraticDefender` | treasure box (rarity 1) |
| ★★ | Adaptive Gene | stat changes inflicted on the Digimon are passed to the Digimon that caused it. | `StatMirror` | deep treasure box (rarity 2) |
| ★★ | Toxic Spore | the Digimon's Physical moves may inflict the Poisoned status. | `ChanceStatusOnCategoryHit` | deep treasure box (rarity 2) |
| ★★★ | Regenerating Ooze | the Digimon's natural HP-recovery speed is boosted. | `FastHealer` | swap shop |

Exchange: Regenerating Ooze for Sludge Skin + Adaptive Gene.

### Unidentified (13 members)

*Chaosmon, Digitamamon and other anomalies; Dark, fast, and hard to pin down.* Representative: Apocalymon, Armageddemon, Chaosmon, Chaosmon VA, Diaboromon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Glitch Ribbon | the Digimon's moves are more intensely affected by type match-ups. | `ErraticAttacker` | treasure box (rarity 1) |
| ★★ | Egg Shell | the Digimon takes reduced damage from multiple attacks in a turn. | `BarrageGuard` | deep treasure box (rarity 2) |
| ★★ | Corrupted Sigil | the Digimon's Dark-type moves have a chance to inflict the Blinker status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Chaos Lens | it allows the Digimon to see foes and items in heavy darkness. | `XRay` | swap shop |

Exchange: Chaos Lens for Glitch Ribbon + Egg Shell.

### Beastkin (12 members)

*Leomon and the beast-men; proud melee fighters who press the advantage.* Representative: BanchoLeomon, Gargomon, GrapLeomon, Lekismon, Leomon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Fang Necklace | the Digimon's regular attack cannot miss. | `SureHitAttacker` | treasure box (rarity 1) |
| ★★ | Sprinter's Anklet | the Digimon's Physical moves may increase the user's Movement Speed. | `StatOnCategoryUse` | deep treasure box (rarity 2) |
| ★★ | Roaring Mane | the Digimon will raise the PP usage of opponents that attack it. | `PressurePlus` | deep treasure box (rarity 2) |
| ★★★ | King's Mane | the Digimon will be able to move again after defeating an enemy. | `Celebrate` | swap shop |

Exchange: King's Mane for Fang Necklace + Sprinter's Anklet.

### Wizard (11 members)

*Wizardmon and the spellcasters; the highest special attack, Dark-leaning.* Representative: Agunimon, Crescemon, Lucemon FM, Lucemon SM, Piedmon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Apprentice Hat | the category of the Digimon's regular attack is changed from physical to special. | `SpecialAttacker` | treasure box (rarity 1) |
| ★★ | Grimoire | the Digimon gets an extra 5PP to all of its moves. | `PPBoost` | deep treasure box (rarity 2) |
| ★★ | Hex Charm | the Digimon's Magical moves may inflict the Confused status. | `ChanceStatusOnCategoryHit` | deep treasure box (rarity 2) |
| ★★★ | Nightmare Tome | the Digimon's Dark-type moves are boosted. | `SecondSTAB` | swap shop |

Exchange: Nightmare Tome for Apprentice Hat + Grimoire.

### Evil (11 members)

*Devimon and the fallen angels; Dark attackers that punish and spread misery.* Representative: Beelzemon, DemiDevimon, Devimon, Goblimon, Guilmon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Wicked Grin | the Digimon's Dark-type moves have a chance to inflict the Cringing status. | `ChanceStatusOnTypeHit` | treasure box (rarity 1) |
| ★★ | Vengeful Pact | it inflicts the Cursed status on the attacker when the Digimon is hit with a Light-type move. | `WeaknessPayback` | deep treasure box (rarity 2) |
| ★★ | Shadow Cloak | the Digimon is more likely to evade attacks from close up. | `CloseDodge` | deep treasure box (rarity 2) |
| ★★★ | Carnage Talon | the Digimon will damage nearby enemies after defeating an enemy. | `ExcessiveForce` | swap shop |

Exchange: Carnage Talon for Wicked Grin + Vengeful Pact.

### Dragonkin (11 members)

*Veemon, Guilmon and the dragon-men; Fire, fast, and always charging in.* Representative: BlackWarGreymon, Cyberdramon, Cyclonemon, Flamedramon, Gaiomon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Spark Bracer | the Digimon's Fire-type moves may lower the target's Defense. | `ChanceStatOnTypeHit` | treasure box (rarity 1) |
| ★★ | Dragon Drive | it changes the Digimon's lunging moves into two weaker strikes. | `DoubleDash` | deep treasure box (rarity 2) |
| ★★ | Rush Scarf | the Digimon will be able to move when charging attacks. | `ChargeWalker` | deep treasure box (rarity 2) |
| ★★★ | Imperial Emblem | the Digimon's regular attacks change to match its type. | `TypedAttack` | swap shop |

Exchange: Imperial Emblem for Spark Bracer + Dragon Drive.

### Puppet (11 members)

*Monzaemon, Puppetmon and the toys; Light-touched special attackers who pull strings.* Representative: Etemon, KingEtemon, Monzaemon, Pandamon, Pumpkinmon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Toy Bell | the Digimon will find more shops when exploring in dungeons. | `ShopFinder` | treasure box (rarity 1) |
| ★★ | Marionette String | the Digimon's regular attack will throw opponents back. | `ThrowOnAttack` | deep treasure box (rarity 2) |
| ★★ | Cotton Stuffing | the Digimon gives back recovered HP when it is healed by another Digimon. | `Gratitude` | deep treasure box (rarity 2) |
| ★★★ | Puppet Strings | the Digimon's regular attacks and thrown items have a chance to inflict the Immobilized status. | `StatusOnAttack` | swap shop |

Exchange: Puppet Strings for Toy Bell + Marionette String.

### Angel (10 members)

*Angemon's line; Light healers and blasters with the best magic in the game.* Representative: Angemon, Angewomon, Kerpymon (Blk), Kerpymon (Good), Lucemon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Vigilant Feather | the Digimon becomes immune to the Asleep status. | `StatusImmune` | treasure box (rarity 1) |
| ★★ | Halo Ring | the Digimon will gradually restore the HP of its allies when its own HP is full. | `RoyalVeil` | deep treasure box (rarity 2) |
| ★★ | Judgment Bell | the Digimon's Light-type moves have a chance to inflict the Paralyzed status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Grace of Heaven | the Digimon will revive a fallen ally when it reaches a new floor. | `AllyReviver` | swap shop |

Exchange: Grace of Heaven for Vigilant Feather + Halo Ring.

### Sea Animal (10 members)

*Seadramon, Gomamon and the ocean dwellers; Water special attackers, slow on land.* Representative: Betamon, Coelamon, Dragomon, Gomamon, Ikkakumon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Fin Guard | the Digimon can traverse water. | `WaterTerrain` | treasure box (rarity 1) |
| ★★ | Harpoon Tooth | items thrown by the Digimon will pierce through enemies. | `MasterHurler` | deep treasure box (rarity 2) |
| ★★ | Kelp Wrap | the Digimon's Water-type moves have a chance to inflict the Immobilized status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Leviathan Pearl | the Digimon's Water-type moves are boosted. | `SecondSTAB` | swap shop |

Exchange: Leviathan Pearl for Fin Guard + Harpoon Tooth.

### Mollusk (10 members)

*Shellmon, Numemon and the slimes; slow, shelled, and fond of treasure.* Representative: BlackKingNumemon, Botamon, Geremon, Numemon, Pabumon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Mucus Coat | the Digimon becomes immune to the Burned status. | `StatusImmune` | treasure box (rarity 1) |
| ★★ | Hard Shell | it prevents the Digimon from fainting to Physical moves, leaving it with 1 HP. | `EndureCategory` | deep treasure box (rarity 2) |
| ★★ | Pearl Lure | the Digimon will find more Treasure Chests when exploring in dungeons. | `ChestFinder` | deep treasure box (rarity 2) |
| ★★★ | Cannon Shell | it changes the Digimon's regular attack into a short projectile. | `ProjectileAttack` | swap shop |

Exchange: Cannon Shell for Mucus Coat + Hard Shell.

### Lesser (10 members)

*The In-Training babies; tiny stats, so their treasures keep them alive and bouncing.* Representative: Bukamon, Koromon, Motimon, Nyaromon, Pagumon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Bubble Wrap | the Digimon will take reduced damage from explosions and splash damage. | `ExplosionGuard` | treasure box (rarity 1) |
| ★★ | Bouncy Ball | the Digimon will more easily dodge attacks if its previous move missed. | `MisfortuneMirror` | deep treasure box (rarity 2) |
| ★★ | Foam Spray | the Digimon's Physical moves may inflict the Blinker status. | `ChanceStatusOnCategoryHit` | deep treasure box (rarity 2) |
| ★★★ | Cradle Blanket | the Digimon is fully healed upon entering a new floor. | `HealOnNewFloor` | swap shop |

Exchange: Cradle Blanket for Bubble Wrap + Bouncy Ball.

### Machine (10 members)

*Hagurumon, Guardromon and the gear-driven; Electric, armoured, and relentless.* Representative: Chaosdramon, Clockmon, Datamon, GroundLocomon, Guardromon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Gear Cog | the Digimon's PP cannot be lowered by the moves and abilities of opposing Digimon. | `PPSaver` | treasure box (rarity 1) |
| ★★ | Static Coil | the Digimon's Electric-type moves have a chance to inflict the Paralyzed status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★ | Crawler Treads | the Digimon can traverse water, lava, and pits. | `AllTerrain` | deep treasure box (rarity 2) |
| ★★★ | Faraday Frame | it reduces damage done to Electric-type members by Earth-type attacks, based on how many are on the team. | `TypeGroupWeaknessReduce` | swap shop |

Exchange: Faraday Frame for Gear Cog + Static Coil.

### Dragonling (10 members)

*Young and small dragons; all Attack and appetite, still growing into their scales.* Representative: Dorugamon, Dorugoramon, DoruGreymon, Ginryumon, Hackmon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Nipping Fang | it allows the Digimon's regular attack to strike twice. | `DoubleAttacker` | treasure box (rarity 1) |
| ★★ | Growth Charm | the Digimon's Physical moves may increase the user's Attack. | `StatOnCategoryUse` | deep treasure box (rarity 2) |
| ★★ | Hot Breath | the Digimon's Physical moves may inflict the Burned status. | `ChanceStatusOnCategoryHit` | deep treasure box (rarity 2) |
| ★★★ | Ember Scale | it reduces damage done by Water-type attacks. | `WeaknessReduce` | swap shop |

Exchange: Ember Scale for Nipping Fang + Growth Charm.

### Bird (9 members)

*Wind fliers; fast special attackers that ride the weather.* Representative: Aquilamon, Birdramon, Biyomon, Crowmon, Falcomon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Wind Vane | the Digimon's Attack Range is increased when the floor has the Wind status. | `AttackRangeInWeather` | treasure box (rarity 1) |
| ★★ | Gale Talon | the Digimon's Wind-type moves may lower the target's Movement Speed. | `ChanceStatOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Stormcaller Plume | the Digimon's Wind-type moves are boosted. | `SecondSTAB` | swap shop |

Exchange: Stormcaller Plume for Wind Vane + Gale Talon.

### Demon Lord (9 members)

*The Seven Great Demon Lords; Dark Megas strong in everything and proud of it.* Representative: Barbamon, Beelzemon, Beelzemon BM, Belphemon RM, Belphemon SM ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Pride Ring | the Digimon cannot have its Special Attack lowered. | `StatDropImmune` | treasure box (rarity 1) |
| ★★ | Gluttony Fang | the Digimon will regain HP after defeating an enemy. | `Absorption` | deep treasure box (rarity 2) |
| ★★★ | Crown of Seven Sins | it reduces damage done by Light-type attacks. | `WeaknessReduce` | swap shop |

Exchange: Crown of Seven Sins for Pride Ring + Gluttony Fang.

### Elemental (9 members)

*Meramon, Frigimon and Gotsumon; living fire, ice and stone, slow and solid.* Representative: BlueMeramon, Frigimon, Golemon, Gotsumon, Icemon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Core Shard | the Digimon can traverse lava without being burned. | `LavaTerrain` | treasure box (rarity 1) |
| ★★ | Elemental Prism | the Digimon's moves are more intensely affected by type match-ups. | `ErraticAttacker` | deep treasure box (rarity 2) |
| ★★★ | Molten Heart | the Digimon's Physical moves inflict the Burned status. | `StatusOnCategoryHit` | swap shop |

Exchange: Molten Heart for Core Shard + Elemental Prism.

### Vegetation (9 members)

*Palmon, Togemon and the plants; rooted, hardy, and spore-scattering.* Representative: Cherrymon, Lalamon, Mushroomon, Palmon, Puppetmon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Rooting Sandals | the Digimon is prevented from being forced off its location. | `Anchor` | treasure box (rarity 1) |
| ★★ | Pollen Puff | the Digimon's Plant-type moves have a chance to inflict the Asleep status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Verdant Crown | the Digimon changes the floor to Grassy Terrain after using a Status move. | `MapStatusOnCategoryUse` | swap shop |

Exchange: Verdant Crown for Rooting Sandals + Pollen Puff.

### Shaman (8 members)

*Masked Megas who call weather and spirits; superb special stats and speed.* Representative: Dianamon, Kuzuhamon, Merukimon, Minervamon, Neptunemon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Spirit Beads | it restores the PP of all moves when the Digimon reaches a new floor. | `DeepBreatherPlus` | treasure box (rarity 1) |
| ★★ | Rain Dance Rattle | the Digimon changes the floor to Rain after using a Status move. | `MapStatusOnCategoryUse` | deep treasure box (rarity 2) |
| ★★★ | Spirit Gate | it partially reveals the floor's layout the Digimon reaches a new floor. | `MapSurveyor` | swap shop |

Exchange: Spirit Gate for Spirit Beads + Rain Dance Rattle.

### Mythical Beast (7 members)

*Airdramon, Pegasusmon and SaberLeomon; Wind-riding beasts of legend, swift above all.* Representative: Airdramon, Gryphonmon, HippoGryphonmon, Kyubimon, SaberLeomon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Cloud Hoof | the Digimon is protected from weather damage. | `WeatherProtection` | treasure box (rarity 1) |
| ★★ | Zephyr Mane | it boosts the Movement Speed of Wind-type members that have no status conditions. | `TypeSpeedBoost` | deep treasure box (rarity 2) |
| ★★★ | Storm Horn | it reduces damage done by Electric-type attacks. | `WeaknessReduce` | swap shop |

Exchange: Storm Horn for Cloud Hoof + Zephyr Mane.

### Undead (7 members)

*SkullGreymon, Bakemon and the risen; Dark bruisers that refuse to stay down.* Representative: Breakdramon, Dracmon, Matadormon, Myotismon, Raremon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Cursed Ash | the Digimon's Dark-type moves have a chance to inflict the Cursed status. | `ChanceStatusOnTypeHit` | treasure box (rarity 1) |
| ★★ | Bone Armor | it prevents the Digimon from fainting to Light-type moves, leaving it with 1 HP. | `EndureType` | deep treasure box (rarity 2) |
| ★★★ | Deathly Lullaby | it inflicts the Asleep status on the attacker when the Digimon is hit with a Light-type move. | `WeaknessPayback` | swap shop |

Exchange: Deathly Lullaby for Cursed Ash + Bone Armor.

### Fairy (7 members)

*Lillymon, Rosemon and the pixies; Plant-aligned casters with the finest magic.* Representative: Lilamon, Lillymon, Lotosmon, MarineAngemon, Piximon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Fae Ribbon | the category of the Digimon's regular attack is changed from physical to special. | `SpecialAttacker` | treasure box (rarity 1) |
| ★★ | Rose Whip | the Digimon's Plant-type moves may lower the target's Defense. | `ChanceStatOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Blossom Tiara | it slightly boosts the Special Attack of Plant-type members. | `TypeStatBonus` | swap shop |

Exchange: Blossom Tiara for Fae Ribbon + Rose Whip.

### Ghost (6 members)

*Bakemon, Phantomon and the haunts; Dark specialists that pass through and bind.* Representative: Bakemon, Myotismon, Phantomon, Raremon, SkullGreymon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Wisp Lantern | the Digimon's moves and items that hit in a straight line will pass through walls. | `PassThroughAttacker` | treasure box (rarity 1) |
| ★★ | Spectral Chain | the Digimon's Dark-type moves have a chance to inflict the Immobilized status. | `ChanceStatusOnTypeHit` | deep treasure box (rarity 2) |
| ★★★ | Veil of the Departed | the Digimon becomes extremely likely to avoid Light-type attacks. | `WeaknessDodge` | swap shop |

Exchange: Veil of the Departed for Wisp Lantern + Spectral Chain.

### Aquatic (6 members)

*Whamon, MarineAngemon and the deep-sea; Water casters that heal in their element.* Representative: MegaSeadramon, MetalSeadramon, Neptunemon, Seadramon, Syakomon ....

| Tier | Item | Effect | PMDO effect | Source |
| --- | --- | --- | --- | --- |
| ★ | Coral Charm | the Digimon recovers HP when in water. | `HealInWater` | treasure box (rarity 1) |
| ★★ | Bubble Pearl | the Digimon gains the Aqua Ring status after using a Magical move. | `StatusOnCategoryUse` | deep treasure box (rarity 2) |
| ★★★ | Abyssal Pearl | it reduces damage done by Plant-type attacks. | `WeaknessReduce` | swap shop |

Exchange: Abyssal Pearl for Coral Charm + Bubble Pearl.

