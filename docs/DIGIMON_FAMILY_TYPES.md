# Digimon family types

Source: `DataAsset/Digimon/digimon_family_types.json` (Digimon Wiki physical types, retrieved 2026-09-13).
This is the family notion the exclusive-item work will use. The Phase 2 lineage families and the
treasure-box TM fallback comment are superseded by it.

## Runtime representation

Every listed wiki type is stored, in wiki order, as `Family_Types` on the Digimon form and
`family_types` in the Lua runtime catalog. The `NO DATA` placeholder is dropped. The summary
screen joins them with a slash. A Digimon with several types belongs to every one of them;
140 of 341 species have more than one type, and the most is four.

## Family sizes

97 distinct types. Membership below counts every type a species carries, so a
multi-type species appears under each of its types. The primary column counts species whose
first listed type is that family.

| Family type | Members | Primary | Species |
| --- | ---: | ---: | --- |
| Cyborg | 36 | 13 | Andromon, Boltmon, CannonBeemon, Cyberdramon, Darkdramon, Ebemon, Gigadramon, HiAndromon, Justimon, KendoGarurumon, MachGaogamon, Machinedramon, MagnaGarurumon, MagnaGarurumon (SV), Megadramon, MetalEtemon, MetalGarurumon, MetalGarurumon (Blk), MetalGreymon, MetalGreymon (Blue), MetalMamemon, MetalSeadramon, MetalTyrannomon, PileVolcamon, Rapidmon, Raptordramon, Raremon, Ravemon, Ravemon BM, RizeGreymon, RustTyranomon, Tankmon, TigerVespamon, Volcanomon, WarGrowlmon, Waspmon |
| Android | 23 | 23 | Andromon, Boltmon, CannonBeemon, Gigadramon, HiAndromon, Justimon, KendoGarurumon, Machinedramon, MagnaGarurumon, Megadramon, MetalEtemon, MetalGarurumon, MetalGreymon, MetalGreymon (Blue), MetalMamemon, MetalSeadramon, MetalTyrannomon, PileVolcamon, Rapidmon, Raptordramon, Tankmon, Volcanomon, WarGrowlmon |
| Holy Warrior | 23 | 23 | Alphamon, Alphamon NX, Alphamon Ouryuken, Craniamon, Crusadermon, Crusadermon NX, Dynasmon, Examon, Gallantmon, Gallantmon CM, Gallantmon NX, Gankoomon, Jesmon, Kentaurosmon, Leopardmon, Leopardmon LM, Leopardmon NX, Magnamon, Omnimon, Omnimon NX, Omnimon Zwart, Rapidmon (Armor), UlforceVeedramon |
| Warrior | 19 | 4 | Alphamon, Alphamon NX, Crusadermon, Crusadermon NX, Dynasmon, Gallantmon, Gallantmon CM, Gallantmon NX, Grademon, Knightmon, Lobomon, Magnamon, Omnimon, Omnimon NX, Rapidmon, Rapidmon (Armor), UlforceVeedramon, Valkyrimon, WarGreymon |
| Animal | 18 | 18 | Chuumon, DoruGreymon, Dorugamon, Dorumon, Gargomon, Garurumon, Gatomon, GrapLeomon, Hououmon, Leomon, Lopmon, Panjyamon, Renamon, Silphymon, Terriermon, Turuiemon, WereGarurumon, WereGarurumon (Blk) |
| Dragon | 15 | 10 | Coredramon (Blue), Coredramon (Green), Cyclonemon, Dorugoramon, Dracomon, Flamedramon, Gaiomon, Ginryumon, Hisyaryumon, Ouryumon, Paildramon, Plesiomon, Ryudamon, Veemon, WarGreymon |
| Insectoid | 14 | 11 | CannonBeemon, FanBeemon, GranKuwagamon, HerculesKabuterimon, Hudiemon, Kabuterimon, Kuwagamon, MegaKabuterimon, Okuwamon, Stingmon, Tentomon, TigerVespamon, TyrantKabuterimon, Waspmon |
| Mutant | 13 | 7 | Apocalymon, CatchMamemon, Dinobeemon, GoldNumemon, Mamemon, MudFrigimon, PlatinumNumemon, PlatinumSukamon, PrinceMamemon, Shakkoumon, Starmon, Sukamon, SuperStarmon |
| Beastkin | 12 | 3 | BanchoLeomon, Gargomon, GrapLeomon, Lekismon, Leomon, Panjyamon, Renamon, Silphymon, Turuiemon, Vikemon, WereGarurumon, WereGarurumon (Blk) |
| Dragonkin | 11 | 5 | BlackWarGreymon, Cyberdramon, Cyclonemon, Flamedramon, Gaiomon, OmniShoutmon, Paildramon, SaviorHuckmon, Slayerdramon, Strikedramon, WarGreymon |
| Puppet | 11 | 11 | Etemon, KingEtemon, Monzaemon, Pandamon, Pumpkinmon, Puppetmon, Sistermon B (Awake.), Sistermon Blanc, Sistermon C (Awake.), Sistermon Ciel, ToyAgumon |
| Wizard | 11 | 6 | Agunimon, Crescemon, Lucemon FM, Lucemon SM, Piedmon, Sakuyamon, Socerimon, Susanomon, Taomon, Wisemon, Wizardmon |
| Angel | 10 | 10 | Angemon, Angewomon, Kerpymon (Blk), Kerpymon (Good), Lucemon, MagnaAngemon, Mastemon, Ophanimon, Seraphimon, Shakkoumon |
| Beast | 10 | 5 | Chuumon, Dorumon, GaoGamon, Gaomon, Garurumon, Garurumon (Blk), Lopmon, Ryudamon, Salamon, Terriermon |
| Lesser | 10 | 8 | Bukamon, Koromon, Motimon, Nyaromon, Pagumon, Tanemon, Tokomon, Tsunomon, Wanyamon, Yokomon |
| Machine | 10 | 9 | Chaosdramon, Clockmon, Datamon, GroundLocomon, Guardromon, Guardromon (Gold), Hagurumon, Machinedramon, MegaGargomon, Solarmon |
| Demon Lord | 9 | 9 | Barbamon, Beelzemon, Beelzemon BM, Belphemon RM, Belphemon SM, Creepymon, Leviamon, Lilithmon, Lucemon FM |
| Dinosaur | 9 | 5 | Ankylomon, BaoHuckmon, GeoGreymon, Greymon, Greymon (Blue), MetalTyrannomon, Monochromon, Triceramon, Tyrannomon |
| Evil | 9 | 5 | Beelzemon, DemiDevimon, Devimon, Goblimon, Guilmon, Impmon, LadyDevimon, Ogremon, VenomMyotismon |
| Vegetation | 9 | 7 | Cherrymon, Lalamon, Mushroomon, Palmon, Puppetmon, Sunflowmon, Togemon, Vegiemon, Woodmon |
| Shaman | 8 | 6 | Dianamon, Kuzuhamon, Merukimon, Minervamon, Neptunemon, Sakuyamon, Susanomon, Titamon |
| Unidentified | 8 | 7 | Apocalymon, Armageddemon, Diaboromon, Infermon, Keramon, Kuramon, Kurisarimon, Tsumemon |
| Fairy | 7 | 7 | Lilamon, Lillymon, Lotosmon, MarineAngemon, Piximon, Rosemon, Rosemon BM |
| Mysterious Beast | 7 | 7 | Arcadiamon Champion, Arcadiamon In-Tr., Arcadiamon Mega, Arcadiamon Rookie, Arcadiamon Ultimate, Arcadiamon Ultra, Kyubimon |
| Sea Animal | 7 | 3 | Dragomon, Gomamon, Ikkakumon, MegaSeadramon, Seadramon, Whamon, Zudomon |
| Undead | 7 | 2 | Breakdramon, Dracmon, Matadormon, Myotismon, Raremon, SkullGreymon, SkullSatamon |
| Aquatic | 6 | 5 | MegaSeadramon, MetalSeadramon, Neptunemon, Seadramon, Syakomon, Whamon |
| Beast Dragon | 6 | 4 | DoruGreymon, Dorugamon, Dorugoramon, Ginryumon, Hisyaryumon, Ouryumon |
| Ghost | 6 | 4 | Bakemon, Myotismon, Phantomon, Raremon, SkullGreymon, SkullSatamon |
| Holy Beast | 6 | 4 | Antylamon, Chirinmon, Gatomon, Hououmon, Kudamon, Reppamon |
| Mammal | 6 | 5 | Armadillomon, Elecmon, Gazimon, Lunamon, Patamon, Salamon |
| Mythical Animal | 5 | 3 | Airdramon, Gryphonmon, Kyubimon, Unimon, Veedramon |
| Reptile | 5 | 4 | Agumon, Agumon (Blk), Gabumon, Gabumon (Blk), Guilmon |
| Abnormal | 4 | 4 | MudFrigimon, PlatinumSukamon, Starmon, Sukamon |
| Amphibian | 4 | 4 | Betamon, Gekomon, Otamamon, ShogunGekomon |
| Bird | 4 | 4 | Aquilamon, Birdramon, Biyomon, Garudamon |
| Dark Animal | 4 | 4 | BlackGatomon, GranDracmon, Sangloupmon, VenomMyotismon |
| Fallen Angel | 4 | 2 | Devimon, IceDevimon, LadyDevimon, SkullSatamon |
| Mini Dragon | 4 | 3 | Hackmon, Monodramon, Shoutmon, Veemon |
| Mollusk | 4 | 4 | BlackKingNumemon, Geremon, Numemon, PlatinumNumemon |
| Mythical Beast | 4 | 1 | Airdramon, Gryphonmon, HippoGryphonmon, Unimon |
| Pixie | 4 | 0 | Lillymon, MarineAngemon, Piximon, Rosemon |
| Slime | 4 | 3 | Botamon, Pabumon, Poyomon, Punimon |
| Ancient Dragon | 3 | 3 | Imperialdramon DM, Imperialdramon FM, Imperialdramon PM |
| Avian | 3 | 3 | Falcomon, Hawkmon, Peckmon |
| Dark Dragon | 3 | 2 | BurningGreymon, Growlmon, Megadramon |
| Demon | 3 | 3 | Goblimon, Ogremon, Titamon |
| Flame | 3 | 1 | BlueMeramon, Meramon, SkullMeramon |
| Holy Dragon | 3 | 3 | AeroVeedramon, Goldramon, Magnadramon |
| Ice-Snow | 3 | 3 | Frigimon, Icemon, Socerimon |
| Mineral | 3 | 2 | Golemon, Gotsumon, Icemon |
| Rock | 3 | 1 | Golemon, Gotsumon, Meteormon |
| Sea Beast | 3 | 0 | Gomamon, Ikkakumon, Zudomon |
| Weapon | 3 | 3 | Duramon, Zubaeagermon, Zubamon |
| Ancient Dragonkin | 2 | 0 | Imperialdramon FM, Imperialdramon PM |
| Ankylosaur | 2 | 2 | Ankylomon, Monochromon |
| Archangel | 2 | 0 | Angewomon, MagnaAngemon |
| Beast Knight | 2 | 2 | MirageGaogamon, MirageGaogamon BM |
| Bulb | 2 | 2 | Tanemon, Yokomon |
| Cherub | 2 | 0 | Kerpymon (Blk), Kerpymon (Good) |
| Composite | 2 | 1 | Machinedramon, Unimon |
| Crustacean | 2 | 1 | ShellNumemon, Syakomon |
| Fire | 2 | 2 | Meramon, SkullMeramon |
| Giant Bird | 2 | 0 | Aquilamon, Birdramon |
| Light Dragon | 2 | 2 | ShineGreymon, ShineGreymon BM |
| Mythical Dragon | 2 | 1 | ExVeemon, Veedramon |
| Unique | 2 | 2 | Chaosmon, Chaosmon VA |
| Alien | 1 | 1 | Vademon |
| Ancient Animal | 1 | 1 | SaberLeomon |
| Ancient Fish | 1 | 1 | Coelamon |
| Ancient Holy Warrior | 1 | 0 | Imperialdramon PM |
| Aquabeast | 1 | 1 | Dragomon |
| Birdkin | 1 | 0 | Garudamon |
| Carnivorous Plant | 1 | 1 | Vegiemon |
| Ceratopsian | 1 | 1 | Triceramon |
| Dark Knight | 1 | 1 | ChaosGallantmon |
| Dark Warrior | 1 | 0 | ChaosGallantmon |
| Demon God | 1 | 1 | Lucemon SM |
| Devil | 1 | 0 | VenomMyotismon |
| Dragon Warrior | 1 | 1 | KaiserGreymon |
| Earth Dragon | 1 | 1 | Groundramon |
| Evil Dragon | 1 | 1 | Megidramon |
| Holy Bird | 1 | 1 | Varodurumon |
| Holy Sword | 1 | 1 | Durandamon |
| Icy | 1 | 0 | Frigimon |
| Invader | 1 | 1 | Nanimon |
| Jellyfish | 1 | 1 | Poyomon |
| Larva | 1 | 1 | Wormmon |
| Machine Dragon | 1 | 1 | Breakdramon |
| Micro | 1 | 0 | Bukamon |
| Mysterious Bird | 1 | 1 | Crowmon |
| Perfect | 1 | 1 | Digitamamon |
| Plesiosaur | 1 | 0 | Plesiomon |
| Seraph | 1 | 0 | Seraphimon |
| Skeleton | 1 | 0 | SkullGreymon |
| Sky Dragon | 1 | 1 | Wingdramon |
| Throne | 1 | 0 | Ophanimon |

## Small families (43 with one or two members)

Candidates to merge into a broader type or drop from the exclusive-item plan. Decision pending.

- **Alien** (1): Vademon
- **Ancient Animal** (1): SaberLeomon
- **Ancient Fish** (1): Coelamon
- **Ancient Holy Warrior** (1): Imperialdramon PM
- **Aquabeast** (1): Dragomon
- **Birdkin** (1): Garudamon
- **Carnivorous Plant** (1): Vegiemon
- **Ceratopsian** (1): Triceramon
- **Dark Knight** (1): ChaosGallantmon
- **Dark Warrior** (1): ChaosGallantmon
- **Demon God** (1): Lucemon SM
- **Devil** (1): VenomMyotismon
- **Dragon Warrior** (1): KaiserGreymon
- **Earth Dragon** (1): Groundramon
- **Evil Dragon** (1): Megidramon
- **Holy Bird** (1): Varodurumon
- **Holy Sword** (1): Durandamon
- **Icy** (1): Frigimon
- **Invader** (1): Nanimon
- **Jellyfish** (1): Poyomon
- **Larva** (1): Wormmon
- **Machine Dragon** (1): Breakdramon
- **Micro** (1): Bukamon
- **Mysterious Bird** (1): Crowmon
- **Perfect** (1): Digitamamon
- **Plesiosaur** (1): Plesiomon
- **Seraph** (1): Seraphimon
- **Skeleton** (1): SkullGreymon
- **Sky Dragon** (1): Wingdramon
- **Throne** (1): Ophanimon
- **Ancient Dragonkin** (2): Imperialdramon FM, Imperialdramon PM
- **Ankylosaur** (2): Ankylomon, Monochromon
- **Archangel** (2): Angewomon, MagnaAngemon
- **Beast Knight** (2): MirageGaogamon, MirageGaogamon BM
- **Bulb** (2): Tanemon, Yokomon
- **Cherub** (2): Kerpymon (Blk), Kerpymon (Good)
- **Composite** (2): Machinedramon, Unimon
- **Crustacean** (2): ShellNumemon, Syakomon
- **Fire** (2): Meramon, SkullMeramon
- **Giant Bird** (2): Aquilamon, Birdramon
- **Light Dragon** (2): ShineGreymon, ShineGreymon BM
- **Mythical Dragon** (2): ExVeemon, Veedramon
- **Unique** (2): Chaosmon, Chaosmon VA
