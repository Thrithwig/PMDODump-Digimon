# Digimon family types

Source: `DataAsset/Digimon/digimon_family_types.json` (Digimon Wiki physical types, retrieved 2026-09-13).
This is the family notion the exclusive-item work uses. The Phase 2 lineage families and the
treasure-box TM fallback comment are superseded by it.

## Runtime representation

Every listed wiki type is stored, in wiki order, as `Family_Types` on the Digimon form and
`family_types` in the Lua runtime catalog. The `NO DATA` placeholder is dropped. The summary
screen joins them with a slash. A Digimon with several types belongs to every one of them.

## Policy

Owner decisions (2026-09-13), in order:

1. Wiki types are merged per the table below (`FAMILY_MERGES` in `Scripts/digimon_runtime_assets.py`).
2. Families with fewer than 4 members are dropped (`MIN_FAMILY_MEMBERS`).
3. A species whose every family was dropped keeps its source types and is listed for a decision.

Apply changes with `python Scripts/digimon_family_types.py`, then rebuild the Monster index.

### Merges

| Family | Merged from |
| --- | --- |
| Beast | Mammal |
| Bird | Avian, Birdkin, Giant Bird, Holy Bird, Mysterious Bird |
| Dragon | Ancient Dragon, Ancient Dragonkin, Dark Dragon, Dragon Warrior, Earth Dragon, Evil Dragon, Holy Dragon, Light Dragon, Machine Dragon, Mythical Dragon, Sky Dragon |
| Dragonling | Beast Dragon, Mini Dragon |
| Elemental | Fire, Flame, Ice-Snow, Icy, Mineral, Rock |
| Evil | Fallen Angel |
| Fairy | Pixie |
| Insectoid | Larva |
| Mollusk | Crustacean, Slime |
| Mutant | Abnormal, Alien |
| Mythical Beast | Ancient Animal, Mythical Animal |
| Reptile | Dinosaur |
| Sea Animal | Ancient Fish |
| Spiritual Beast | Dark Animal, Holy Beast, Mysterious Beast |
| Unidentified | Invader, Perfect, Unique |
| Warrior | Beast Knight, Dark Knight, Dark Warrior, Holy Sword, Weapon |

## Families (33)

| Family | Members | Species |
| --- | ---: | --- |
| Cyborg | 36 | Andromon, Boltmon, CannonBeemon, Cyberdramon, Darkdramon, Ebemon, Gigadramon, HiAndromon, Justimon, KendoGarurumon, MachGaogamon, Machinedramon, MagnaGarurumon, MagnaGarurumon (SV), Megadramon, MetalEtemon, MetalGarurumon, MetalGarurumon (Blk), MetalGreymon, MetalGreymon (Blue), MetalMamemon, MetalSeadramon, MetalTyrannomon, PileVolcamon, Rapidmon, Raptordramon, Raremon, Ravemon, Ravemon BM, RizeGreymon, RustTyranomon, Tankmon, TigerVespamon, Volcanomon, WarGrowlmon, Waspmon |
| Dragon | 33 | AeroVeedramon, Breakdramon, BurningGreymon, Coredramon (Blue), Coredramon (Green), Cyclonemon, Dorugoramon, Dracomon, ExVeemon, Flamedramon, Gaiomon, Ginryumon, Goldramon, Groundramon, Growlmon, Hisyaryumon, Imperialdramon DM, Imperialdramon FM, Imperialdramon PM, KaiserGreymon, Magnadramon, Megadramon, Megidramon, Ouryumon, Paildramon, Plesiomon, Ryudamon, ShineGreymon, ShineGreymon BM, Veedramon, Veemon, WarGreymon, Wingdramon |
| Warrior | 26 | Alphamon, Alphamon NX, ChaosGallantmon, Crusadermon, Crusadermon NX, Duramon, Durandamon, Dynasmon, Gallantmon, Gallantmon CM, Gallantmon NX, Grademon, Knightmon, Lobomon, Magnamon, MirageGaogamon, MirageGaogamon BM, Omnimon, Omnimon NX, Rapidmon, Rapidmon (Armor), UlforceVeedramon, Valkyrimon, WarGreymon, Zubaeagermon, Zubamon |
| Android | 23 | Andromon, Boltmon, CannonBeemon, Gigadramon, HiAndromon, Justimon, KendoGarurumon, Machinedramon, MagnaGarurumon, Megadramon, MetalEtemon, MetalGarurumon, MetalGreymon, MetalGreymon (Blue), MetalMamemon, MetalSeadramon, MetalTyrannomon, PileVolcamon, Rapidmon, Raptordramon, Tankmon, Volcanomon, WarGrowlmon |
| Holy Warrior | 23 | Alphamon, Alphamon NX, Alphamon Ouryuken, Craniamon, Crusadermon, Crusadermon NX, Dynasmon, Examon, Gallantmon, Gallantmon CM, Gallantmon NX, Gankoomon, Jesmon, Kentaurosmon, Leopardmon, Leopardmon LM, Leopardmon NX, Magnamon, Omnimon, Omnimon NX, Omnimon Zwart, Rapidmon (Armor), UlforceVeedramon |
| Animal | 18 | Chuumon, DoruGreymon, Dorugamon, Dorumon, Gargomon, Garurumon, Gatomon, GrapLeomon, Hououmon, Leomon, Lopmon, Panjyamon, Renamon, Silphymon, Terriermon, Turuiemon, WereGarurumon, WereGarurumon (Blk) |
| Spiritual Beast | 17 | Antylamon, Arcadiamon Champion, Arcadiamon In-Tr., Arcadiamon Mega, Arcadiamon Rookie, Arcadiamon Ultimate, Arcadiamon Ultra, BlackGatomon, Chirinmon, Gatomon, GranDracmon, Hououmon, Kudamon, Kyubimon, Reppamon, Sangloupmon, VenomMyotismon |
| Reptile | 16 | Agumon, Agumon (Blk), Ankylomon, BaoHuckmon, Gabumon, Gabumon (Blk), Gekomon, GeoGreymon, Greymon, Greymon (Blue), Guilmon, MetalTyrannomon, Monochromon, ShogunGekomon, Triceramon, Tyrannomon |
| Beast | 15 | Armadillomon, Chuumon, Dorumon, Elecmon, GaoGamon, Gaomon, Garurumon, Garurumon (Blk), Gazimon, Lopmon, Lunamon, Patamon, Ryudamon, Salamon, Terriermon |
| Insectoid | 15 | CannonBeemon, FanBeemon, GranKuwagamon, HerculesKabuterimon, Hudiemon, Kabuterimon, Kuwagamon, MegaKabuterimon, Okuwamon, Stingmon, Tentomon, TigerVespamon, TyrantKabuterimon, Waspmon, Wormmon |
| Mutant | 14 | Apocalymon, CatchMamemon, Dinobeemon, GoldNumemon, Mamemon, MudFrigimon, PlatinumNumemon, PlatinumSukamon, PrinceMamemon, Shakkoumon, Starmon, Sukamon, SuperStarmon, Vademon |
| Unidentified | 13 | Apocalymon, Armageddemon, Chaosmon, Chaosmon VA, Diaboromon, Digitamamon, Infermon, Keramon, Kuramon, Kurisarimon, Nanimon, Tsumemon, Vademon |
| Beastkin | 12 | BanchoLeomon, Gargomon, GrapLeomon, Lekismon, Leomon, Panjyamon, Renamon, Silphymon, Turuiemon, Vikemon, WereGarurumon, WereGarurumon (Blk) |
| Dragonkin | 11 | BlackWarGreymon, Cyberdramon, Cyclonemon, Flamedramon, Gaiomon, OmniShoutmon, Paildramon, SaviorHuckmon, Slayerdramon, Strikedramon, WarGreymon |
| Evil | 11 | Beelzemon, DemiDevimon, Devimon, Goblimon, Guilmon, IceDevimon, Impmon, LadyDevimon, Ogremon, SkullSatamon, VenomMyotismon |
| Puppet | 11 | Etemon, KingEtemon, Monzaemon, Pandamon, Pumpkinmon, Puppetmon, Sistermon B (Awake.), Sistermon Blanc, Sistermon C (Awake.), Sistermon Ciel, ToyAgumon |
| Wizard | 11 | Agunimon, Crescemon, Lucemon FM, Lucemon SM, Piedmon, Sakuyamon, Socerimon, Susanomon, Taomon, Wisemon, Wizardmon |
| Angel | 10 | Angemon, Angewomon, Kerpymon (Blk), Kerpymon (Good), Lucemon, MagnaAngemon, Mastemon, Ophanimon, Seraphimon, Shakkoumon |
| Dragonling | 10 | DoruGreymon, Dorugamon, Dorugoramon, Ginryumon, Hackmon, Hisyaryumon, Monodramon, Ouryumon, Shoutmon, Veemon |
| Lesser | 10 | Bukamon, Koromon, Motimon, Nyaromon, Pagumon, Tanemon, Tokomon, Tsunomon, Wanyamon, Yokomon |
| Machine | 10 | Chaosdramon, Clockmon, Datamon, GroundLocomon, Guardromon, Guardromon (Gold), Hagurumon, Machinedramon, MegaGargomon, Solarmon |
| Mollusk | 10 | BlackKingNumemon, Botamon, Geremon, Numemon, Pabumon, PlatinumNumemon, Poyomon, Punimon, ShellNumemon, Syakomon |
| Sea Animal | 10 | Betamon, Coelamon, Dragomon, Gomamon, Ikkakumon, MegaSeadramon, Otamamon, Seadramon, Whamon, Zudomon |
| Bird | 9 | Aquilamon, Birdramon, Biyomon, Crowmon, Falcomon, Garudamon, Hawkmon, Peckmon, Varodurumon |
| Demon Lord | 9 | Barbamon, Beelzemon, Beelzemon BM, Belphemon RM, Belphemon SM, Creepymon, Leviamon, Lilithmon, Lucemon FM |
| Elemental | 9 | BlueMeramon, Frigimon, Golemon, Gotsumon, Icemon, Meramon, Meteormon, SkullMeramon, Socerimon |
| Vegetation | 9 | Cherrymon, Lalamon, Mushroomon, Palmon, Puppetmon, Sunflowmon, Togemon, Vegiemon, Woodmon |
| Shaman | 8 | Dianamon, Kuzuhamon, Merukimon, Minervamon, Neptunemon, Sakuyamon, Susanomon, Titamon |
| Fairy | 7 | Lilamon, Lillymon, Lotosmon, MarineAngemon, Piximon, Rosemon, Rosemon BM |
| Mythical Beast | 7 | Airdramon, Gryphonmon, HippoGryphonmon, Kyubimon, SaberLeomon, Unimon, Veedramon |
| Undead | 7 | Breakdramon, Dracmon, Matadormon, Myotismon, Raremon, SkullGreymon, SkullSatamon |
| Aquatic | 6 | MegaSeadramon, MetalSeadramon, Neptunemon, Seadramon, Syakomon, Whamon |
| Ghost | 6 | Bakemon, Myotismon, Phantomon, Raremon, SkullGreymon, SkullSatamon |

## Dropped families (19)

Ancient Holy Warrior (0), Ankylosaur (0), Aquabeast (0), Archangel (0), Bulb (0), Carnivorous Plant (0), Ceratopsian (0), Cherub (0), Composite (0), Demon (0), Demon God (0), Devil (0), Jellyfish (0), Micro (0), Plesiosaur (0), Sea Beast (0), Seraph (0), Skeleton (0), Throne (0)

## Digimon with no remaining family (0)

None.
