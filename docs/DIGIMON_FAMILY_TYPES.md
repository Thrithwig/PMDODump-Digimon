# Digimon family types

Source: `DataAsset/Digimon/digimon_family_types.json` (Digimon Wiki physical types, retrieved 2026-09-13).
This is the family notion the exclusive-item work uses. The Phase 2 lineage families and the
treasure-box TM fallback comment are superseded by it.

## Runtime representation

Every listed wiki type is stored, in wiki order, as `Family_Types` on the Digimon form and
`family_types` in the Lua runtime catalog. The `NO DATA` placeholder is dropped. The summary
screen joins them with a slash. A Digimon with several types belongs to every one of them.

## Small-family rule

Owner decision (2026-09-13): types with three or fewer members are not used. That removes 54
of 97 wiki types and leaves 43. The rule lives in `Scripts/digimon_runtime_assets.py`
as `MIN_FAMILY_MEMBERS`, so a regeneration reproduces it.

## Kept families (43)

| Family type | Members | Species |
| --- | ---: | --- |
| Cyborg | 36 | Andromon, Boltmon, CannonBeemon, Cyberdramon, Darkdramon, Ebemon, Gigadramon, HiAndromon, Justimon, KendoGarurumon, MachGaogamon, Machinedramon, MagnaGarurumon, MagnaGarurumon (SV), Megadramon, MetalEtemon, MetalGarurumon, MetalGarurumon (Blk), MetalGreymon, MetalGreymon (Blue), MetalMamemon, MetalSeadramon, MetalTyrannomon, PileVolcamon, Rapidmon, Raptordramon, Raremon, Ravemon, Ravemon BM, RizeGreymon, RustTyranomon, Tankmon, TigerVespamon, Volcanomon, WarGrowlmon, Waspmon |
| Android | 23 | Andromon, Boltmon, CannonBeemon, Gigadramon, HiAndromon, Justimon, KendoGarurumon, Machinedramon, MagnaGarurumon, Megadramon, MetalEtemon, MetalGarurumon, MetalGreymon, MetalGreymon (Blue), MetalMamemon, MetalSeadramon, MetalTyrannomon, PileVolcamon, Rapidmon, Raptordramon, Tankmon, Volcanomon, WarGrowlmon |
| Holy Warrior | 23 | Alphamon, Alphamon NX, Alphamon Ouryuken, Craniamon, Crusadermon, Crusadermon NX, Dynasmon, Examon, Gallantmon, Gallantmon CM, Gallantmon NX, Gankoomon, Jesmon, Kentaurosmon, Leopardmon, Leopardmon LM, Leopardmon NX, Magnamon, Omnimon, Omnimon NX, Omnimon Zwart, Rapidmon (Armor), UlforceVeedramon |
| Warrior | 19 | Alphamon, Alphamon NX, Crusadermon, Crusadermon NX, Dynasmon, Gallantmon, Gallantmon CM, Gallantmon NX, Grademon, Knightmon, Lobomon, Magnamon, Omnimon, Omnimon NX, Rapidmon, Rapidmon (Armor), UlforceVeedramon, Valkyrimon, WarGreymon |
| Animal | 18 | Chuumon, DoruGreymon, Dorugamon, Dorumon, Gargomon, Garurumon, Gatomon, GrapLeomon, Hououmon, Leomon, Lopmon, Panjyamon, Renamon, Silphymon, Terriermon, Turuiemon, WereGarurumon, WereGarurumon (Blk) |
| Dragon | 15 | Coredramon (Blue), Coredramon (Green), Cyclonemon, Dorugoramon, Dracomon, Flamedramon, Gaiomon, Ginryumon, Hisyaryumon, Ouryumon, Paildramon, Plesiomon, Ryudamon, Veemon, WarGreymon |
| Insectoid | 14 | CannonBeemon, FanBeemon, GranKuwagamon, HerculesKabuterimon, Hudiemon, Kabuterimon, Kuwagamon, MegaKabuterimon, Okuwamon, Stingmon, Tentomon, TigerVespamon, TyrantKabuterimon, Waspmon |
| Mutant | 13 | Apocalymon, CatchMamemon, Dinobeemon, GoldNumemon, Mamemon, MudFrigimon, PlatinumNumemon, PlatinumSukamon, PrinceMamemon, Shakkoumon, Starmon, Sukamon, SuperStarmon |
| Beastkin | 12 | BanchoLeomon, Gargomon, GrapLeomon, Lekismon, Leomon, Panjyamon, Renamon, Silphymon, Turuiemon, Vikemon, WereGarurumon, WereGarurumon (Blk) |
| Dragonkin | 11 | BlackWarGreymon, Cyberdramon, Cyclonemon, Flamedramon, Gaiomon, OmniShoutmon, Paildramon, SaviorHuckmon, Slayerdramon, Strikedramon, WarGreymon |
| Puppet | 11 | Etemon, KingEtemon, Monzaemon, Pandamon, Pumpkinmon, Puppetmon, Sistermon B (Awake.), Sistermon Blanc, Sistermon C (Awake.), Sistermon Ciel, ToyAgumon |
| Wizard | 11 | Agunimon, Crescemon, Lucemon FM, Lucemon SM, Piedmon, Sakuyamon, Socerimon, Susanomon, Taomon, Wisemon, Wizardmon |
| Angel | 10 | Angemon, Angewomon, Kerpymon (Blk), Kerpymon (Good), Lucemon, MagnaAngemon, Mastemon, Ophanimon, Seraphimon, Shakkoumon |
| Beast | 10 | Chuumon, Dorumon, GaoGamon, Gaomon, Garurumon, Garurumon (Blk), Lopmon, Ryudamon, Salamon, Terriermon |
| Lesser | 10 | Bukamon, Koromon, Motimon, Nyaromon, Pagumon, Tanemon, Tokomon, Tsunomon, Wanyamon, Yokomon |
| Machine | 10 | Chaosdramon, Clockmon, Datamon, GroundLocomon, Guardromon, Guardromon (Gold), Hagurumon, Machinedramon, MegaGargomon, Solarmon |
| Demon Lord | 9 | Barbamon, Beelzemon, Beelzemon BM, Belphemon RM, Belphemon SM, Creepymon, Leviamon, Lilithmon, Lucemon FM |
| Dinosaur | 9 | Ankylomon, BaoHuckmon, GeoGreymon, Greymon, Greymon (Blue), MetalTyrannomon, Monochromon, Triceramon, Tyrannomon |
| Evil | 9 | Beelzemon, DemiDevimon, Devimon, Goblimon, Guilmon, Impmon, LadyDevimon, Ogremon, VenomMyotismon |
| Vegetation | 9 | Cherrymon, Lalamon, Mushroomon, Palmon, Puppetmon, Sunflowmon, Togemon, Vegiemon, Woodmon |
| Shaman | 8 | Dianamon, Kuzuhamon, Merukimon, Minervamon, Neptunemon, Sakuyamon, Susanomon, Titamon |
| Unidentified | 8 | Apocalymon, Armageddemon, Diaboromon, Infermon, Keramon, Kuramon, Kurisarimon, Tsumemon |
| Fairy | 7 | Lilamon, Lillymon, Lotosmon, MarineAngemon, Piximon, Rosemon, Rosemon BM |
| Mysterious Beast | 7 | Arcadiamon Champion, Arcadiamon In-Tr., Arcadiamon Mega, Arcadiamon Rookie, Arcadiamon Ultimate, Arcadiamon Ultra, Kyubimon |
| Sea Animal | 7 | Dragomon, Gomamon, Ikkakumon, MegaSeadramon, Seadramon, Whamon, Zudomon |
| Undead | 7 | Breakdramon, Dracmon, Matadormon, Myotismon, Raremon, SkullGreymon, SkullSatamon |
| Aquatic | 6 | MegaSeadramon, MetalSeadramon, Neptunemon, Seadramon, Syakomon, Whamon |
| Beast Dragon | 6 | DoruGreymon, Dorugamon, Dorugoramon, Ginryumon, Hisyaryumon, Ouryumon |
| Ghost | 6 | Bakemon, Myotismon, Phantomon, Raremon, SkullGreymon, SkullSatamon |
| Holy Beast | 6 | Antylamon, Chirinmon, Gatomon, Hououmon, Kudamon, Reppamon |
| Mammal | 6 | Armadillomon, Elecmon, Gazimon, Lunamon, Patamon, Salamon |
| Mythical Animal | 5 | Airdramon, Gryphonmon, Kyubimon, Unimon, Veedramon |
| Reptile | 5 | Agumon, Agumon (Blk), Gabumon, Gabumon (Blk), Guilmon |
| Abnormal | 4 | MudFrigimon, PlatinumSukamon, Starmon, Sukamon |
| Amphibian | 4 | Betamon, Gekomon, Otamamon, ShogunGekomon |
| Bird | 4 | Aquilamon, Birdramon, Biyomon, Garudamon |
| Dark Animal | 4 | BlackGatomon, GranDracmon, Sangloupmon, VenomMyotismon |
| Fallen Angel | 4 | Devimon, IceDevimon, LadyDevimon, SkullSatamon |
| Mini Dragon | 4 | Hackmon, Monodramon, Shoutmon, Veemon |
| Mollusk | 4 | BlackKingNumemon, Geremon, Numemon, PlatinumNumemon |
| Mythical Beast | 4 | Airdramon, Gryphonmon, HippoGryphonmon, Unimon |
| Pixie | 4 | Lillymon, MarineAngemon, Piximon, Rosemon |
| Slime | 4 | Botamon, Pabumon, Poyomon, Punimon |

## Removed families (54)

Alien (1), Ancient Animal (1), Ancient Dragon (3), Ancient Dragonkin (2), Ancient Fish (1), Ancient Holy Warrior (1), Ankylosaur (2), Aquabeast (1), Archangel (2), Avian (3), Beast Knight (2), Birdkin (1), Bulb (2), Carnivorous Plant (1), Ceratopsian (1), Cherub (2), Composite (2), Crustacean (2), Dark Dragon (3), Dark Knight (1), Dark Warrior (1), Demon (3), Demon God (1), Devil (1), Dragon Warrior (1), Earth Dragon (1), Evil Dragon (1), Fire (2), Flame (3), Giant Bird (2), Holy Bird (1), Holy Dragon (3), Holy Sword (1), Ice-Snow (3), Icy (1), Invader (1), Jellyfish (1), Larva (1), Light Dragon (2), Machine Dragon (1), Micro (1), Mineral (3), Mysterious Bird (1), Mythical Dragon (2), Perfect (1), Plesiosaur (1), Rock (3), Sea Beast (3), Seraph (1), Skeleton (1), Sky Dragon (1), Throne (1), Unique (2), Weapon (3)

## Digimon with no remaining family (44) - decision pending

Every type these species carry was removed. They keep their source types for now so the runtime
check stays green and nothing is silently reclassified. Options: assign each to an existing kept
family, restore one removed family for them, or leave them without family items.

| Digimon | Source types |
| --- | --- |
| AeroVeedramon | Holy Dragon |
| BlueMeramon | Flame |
| BurningGreymon | Dark Dragon |
| ChaosGallantmon | Dark Knight, Dark Warrior |
| Chaosmon | Unique |
| Chaosmon VA | Unique |
| Coelamon | Ancient Fish |
| Crowmon | Mysterious Bird |
| Digitamamon | Perfect |
| Duramon | Weapon |
| Durandamon | Holy Sword |
| ExVeemon | Mythical Dragon |
| Falcomon | Avian |
| Frigimon | Ice-Snow, Icy |
| Goldramon | Holy Dragon |
| Golemon | Mineral, Rock |
| Gotsumon | Mineral, Rock |
| Groundramon | Earth Dragon |
| Growlmon | Dark Dragon |
| Hawkmon | Avian |
| Icemon | Ice-Snow, Mineral |
| Imperialdramon DM | Ancient Dragon |
| Imperialdramon FM | Ancient Dragon, Ancient Dragonkin |
| Imperialdramon PM | Ancient Dragon, Ancient Dragonkin, Ancient Holy Warrior |
| KaiserGreymon | Dragon Warrior |
| Magnadramon | Holy Dragon |
| Megidramon | Evil Dragon |
| Meramon | Fire, Flame |
| Meteormon | Rock |
| MirageGaogamon | Beast Knight |
| MirageGaogamon BM | Beast Knight |
| Nanimon | Invader |
| Peckmon | Avian |
| SaberLeomon | Ancient Animal |
| ShellNumemon | Crustacean |
| ShineGreymon | Light Dragon |
| ShineGreymon BM | Light Dragon |
| SkullMeramon | Fire, Flame |
| Vademon | Alien |
| Varodurumon | Holy Bird |
| Wingdramon | Sky Dragon |
| Wormmon | Larva |
| Zubaeagermon | Weapon |
| Zubamon | Weapon |
