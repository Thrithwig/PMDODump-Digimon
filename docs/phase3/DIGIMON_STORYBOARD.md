# Phase 3 storyboard: The Way Home

Design draft, 12 September 2026. **Story design only: no dialogue, maps, encounters, unlocks or save flags are implemented by this document.** The inventory is **35 released zone containers: 34 expedition/challenge zones and the Guildmaster Island hub container**, not 35 conventional dungeons. Current internal IDs remain stable where proposed display names change.

## Premise and player promise

The island's roads are forgetting where home is. A delivery path becomes a maze overnight; a rescue beacon repeats a message from somebody already safe. Your adventuring party joins a rescue cooperative to reconnect the settlements. Each expedition answers a practical question: who needs help, what can we bring back, and who will be waiting when we return?

The **Return Protocol** is an emergency routing system at **Infinity Summit**, the top of Infinity Mountain. Before the crisis it successfully brought stranded travelers home. **Beelzemon seized it and deliberately rewrote its routes into loops**, trapping residents and amplifying fear, anger, envy and despair. He intends this negative energy to awaken his six fellow Demon Lords: Lilithmon, Barbamon, Belphemon Rage Mode, Daemon, Leviamon and Lucemon Chaos Mode. Together the seven could dominate the Digital World. Unknown to Beelzemon, discarded negative data is also gathering into **Apocalymon**, the postgame threat. These are authored adaptation choices, not claims about canon geography or powers.

**Guardromon is a displaced operator and witness, not the antagonist.** After Tropical Jungle is cleared, it finally descends Infinity Mountain and reaches File Town. It knows who seized the protocol but not why. Its shame at failing to protect the station makes its early account hesitant. Rescue testimony gradually fills the gaps. Residents’ flaws are vulnerabilities Beelzemon exploits, never proof they deserved to be trapped; empathy and practical help allow them to act again.

**The repeated loop is: accept a concrete request at camp → enter its dungeon → rescue somebody or solve the obstruction → return to the commissioning camp → see the result and choose another request.** Combat clears dangerous opponents and security patrols. A rescue can resolve in a scene at an existing endpoint; escort AI is not a new requirement. Small individual rescues build trust before the finale asks all camps to coordinate.

Community rebuilding and close partner relationships evoke earlier Digimon adventures, but the plot and resident personalities here are original proposals, not canon claims. The player is a Digimon adventurer. No mandatory human revelation, chosen-one species, or fixed partner is needed.

## Gameplay boundaries

- Any roster or permanent evolution line can carry every main beat. Use team names/nicknames; never require a specific species, stage, attribute, passive, or move.
- Scan Data restores party members through the existing terminal at its existing cost. Rescued residents choose to settle or reopen a service; they are not free party recruits. A resident and a recruited Digimon of the same species are distinct individuals.
- Permanent digivolution/dedigivolution remains at the Tree of Life with existing item/fusion requirements, level reset, and retained stats. No story requirements are added to evolution. No temporary battle evolution.
- Existing EXP rules, recipient-stage bonuses, PP, loot and failure rules remain intact. No compulsory training minigame, timed mission, resource quota, elemental key, friendship grind, or new battle subsystem is needed for the ending. Named repair components are narrative completion flags, not proposed inventory gates.
- Failing or escaping leaves the request available; no real-time death countdown. Completion/debrief rewards must be one-time and recoverable after an interrupted scene.
- Static transparent Digimon art is sufficient. Phase 4 art and terminal reskins remain separate; no audio conversion is proposed.

## Camps and travel

| Existing ID/location | Proposed display name | Community function and visible aftermath |
|---|---|---|
| `base_camp`, `base_camp_2` / Base Camp | File Town | Rescue headquarters. Empty benches fill with returned travelers; opening and ending share the ordinary meal table. |
| `forest_camp` / Forest Camp | Native Forest Camp | Nursery, food and Tree of Life. Repaired shutters, delivered letters and occupied beds show progress. |
| `cliff_camp` / Cliff Camp | Panorama Camp | Couriers and weather watch. A blank board gains reliable return times. |
| `canyon_camp` / Ravine Camp | Great Canyon Camp | Workshop and water distribution. Salvage becomes repair rather than destruction. |
| `rest_stop` / Cave Shelter | Misty Shelter | Communication refuge. Overlapping distress calls become a roster of people accounted for. |
| `final_stop` / Blizzard Camp | Freezeland Camp | Last staffed shelter. Earlier communities supply its final rescue operation. |
| `guild_hut` / Guild Hut | Guild Office | Archives and optional expeditions. Never a global all-dungeon bypass. |
| `post_office` / Post Office | Post House | Requests, recovered names and ordinary mail. |
| `guildmaster_summit` / Summit | Infinity Summit | Finale rescue site and later memorial; the story still ends back home. |

Keep Base Camp's **three junction routes only**: Guildmaster Trail, Tropical Path and Faultline Ridge. Tropical gives Forest access; Faultline requires that access and opens Trickster Woods. Do not restore Base ferry dungeon entries. Other normal camp groupings follow `docs/DIGIMON_DUNGEON_PROGRESS.md`; Cave of Whispers remains at Misty Shelter.

Tropical's first arrival at Forest introduces the rescued nursery, then explicitly returns to File Town for debrief; safe Forest travel remains available. Likewise, physically reaching another camp can introduce it before the return to the commissioning camp. Current forward-exit callbacks will need later reconciliation: these returns are proposed, not already implemented.

Seven released routes outside the current normal lists get **proposed local dispatch contacts**, not new Base exits: Training Maze, Lava Floe Island and Castaway Cave at Panorama; Eon Island and Prism Isles at Native Forest; Labyrinth of the Lost and The NeverEnding Tale at Great Canyon Camp. Existing camp interiors/contact menus suffice; no new camp map is needed. Their current menu accessibility is not assumed.

## Deliberate resident cast

These replace the current deterministic placeholder assignments. Preserve internal entity IDs and quest state when eventually binding the new presentation. Role-based entries are honest binding targets, not invented legacy entity names. Most service residents are Champion or lower; **Mamemon is the user's explicit Ultimate-stage exception**.

| Current entity or service role | Proposed Digimon / camp | Personality and function |
|---|---|---|
| `Noctowl`, Base/Guild Hut/Summit guide | Clockmon / File Town and Guild Office | Knows appointment times, underestimates danger. Learns to promise honest updates instead of impossible rescue deadlines. Guide and dispatcher, not an oracle. |
| Explosive box opener, previously Voltorb according to playtest; exact entity to bind later | Mamemon / Great Canyon, visiting File Town desk | Meticulous explosives specialist who apologizes to damaged hinges. Uses controlled charges and inventory lists. Existing box-opening service; precision expresses care. |
| `forest_camp:Snorlax` storehouse blocker | Monzaemon / Native Forest | Exhausted after protecting the nursery, retreating into slothful sleep and insisting someone else must handle everything now. Existing challenge becomes a consensual safety test before relief workers take over. Victory opens the building; loss allows retry. Keeps the previously requested species. |
| Forest elder / Tree guidance | Sunflowmon / Native Forest | Practical nursery organizer; judges heroes by who actually comes home. Teaches evolution without story gates. |
| Forest parent and child roles | Gatomon and Nyaromon / Native Forest | An anxious parent and a child who maps low spaces adults overlook. Reunion is Tiny Tunnel's payoff. |
| Forest courier/speedster roles | Terriermon and Lopmon / Native Forest | One rushes to reassure; one checks facts. Learn a shared dispatch/check-in routine. |
| Base coast, entrance and unlucky roles | Gomamon, Goblimon, ToyAgumon / File Town | Expedition planner, calm queue steward and resilient repair apprentice. Goblimon de-escalates arguments; ToyAgumon is not a perpetual punchline. |
| Cliff travel and training contacts | Aquilamon and Hawkmon / Panorama | A flight captain terrified of blame and an impatient apprentice ashamed of needing help. Voluntary preparation replaces proving courage through recklessness. |
| Ravine workshop/tutor and water roles | Hagurumon and Tankmon / Great Canyon | Records keeper and drinking-water transporter. Their everyday complaints reveal the cost of the closures. |
| Cave communication/rest roles | Wizardmon and Gotsumon / Misty | Wizardmon obsessively rechecks calls for fear of abandoning anyone; Gotsumon angrily counts failures instead of asking for help. |
| Blizzard coordinator and late visitor | Frigimon and Guardromon / Freezeland | Frigimon runs kitchen and evacuation list. Frigimon hides exhaustion behind brittle orders. Guardromon, the displaced operator, joins the final preparations after reporting at File Town early in the story. |
| Summit `Xatu` oracle role | Unimon / Infinity Summit | Fallible beacon technician. Knows the manual release, cannot guarantee safety, asks the party to rescue the workers first. |
| Generic shop, storage, assembly and post roles | Chuumon, Armadillomon, Renamon, Falcomon | Exacting quartermaster, dependable stores keeper, quiet roster coordinator and postal worker. Give duplicate species distinct nicknames; retain service behavior and stock. |

Other ambient slots become named mission clients below rather than another random cast. A future binding audit must enumerate each actual entity before changing scripts. Mission visitors can exceed the camp stage guideline (for example Triceramon's weather team). Cast identity never follows the player's current party species.

## Act storyboard

### Opening — the first route home

Clockmon drops its grand welcome because the nursery courier missed check-in. In Tropical Jungle, Falcomon’s terror for Botamon and Punimon makes it reject every possible exit. The party shelters them and clears the route, proving an ordinary rescue can reconnect a path. Native Forest residents remain anxious despite the newcomers’ success. Back in File Town, the first debrief is interrupted by Guardromon descending Infinity Mountain: “Beelzemon has the Return Protocol. It used to bring us home. I do not know what he wants now.” The next request remains bedding and missing mail, not a demand to defeat a Mega immediately.

### Act I — a path is more than a promise

Native Forest’s family, food and mail rescues show different reactions to captivity: Lopmon endlessly rechecks addresses; Gatomon blames every passerby; Monzaemon has exhausted itself protecting everyone and now refuses to get up. Their second conversations change only after the relevant rescue/debrief. Drill Tunnel opens passage toward Signpost Forest, where Impmon’s bad signs concealed travelers from hijacked patrols. Guardromon recognizes the protocol’s seal. Nobody yet knows the purpose of the emotional pressure. Calm Goblimon is a rare, deliberately funny exception who makes space for everyone else’s panic.

### Act II — what the loops are feeding

Panorama’s couriers and Great Canyon’s workers are trapped by blame, pride and scarcity. The quarry records establish deliberate tampering rather than an operator’s mistake. In Great Canyon Basin, Tankmon reports Leviamon rising out of the depths and flying toward Infinity Mountain. At the return debrief, Guardromon recognizes a Demon Lord once thought dormant. It suspects six awakenings fed by negative energy but has incomplete records. Other names emerge from later rescues; the player does not receive a complete villain lecture at the opening. Mamemon’s careful preservation of a damaged log matters more than an explosion.

### Act III — the six answer

After BOTH quarry and basin debriefs, the main routes become Demon Lord confrontations with residents still at their heart. Thunder Pass exposes Daemon’s provoked anger and Barbamon’s tribute racket; Misty Ridge exposes Lilithmon’s isolating promises. These two routes may be completed in either order, and each debrief names only the opponents actually met. Their joined evidence confirms the awakening plan. Freezeland Path confronts Belphemon Rage Mode and rescues exhausted supply workers. Infinity Approach confronts Leviamon and then Lucemon Chaos Mode, completing the six reveals. Each boss defeat breaks a local hold; it does not magically erase everyone’s ordinary anxiety. The last expedition is planned at Freezeland’s kitchen table with help from every reconnected camp.

### Finale — Infinity Mountain

Beelzemon guards the established Guildmaster ascent, now displayed as Infinity Mountain. At the summit, Unimon and other trapped workers need rescuing while Beelzemon tries to bind the restored routes to his command. The normal final encounter gives the workers time to isolate his alterations and restore the original emergency routing function with local check-ins. Guardromon assists over the reopened network, never as a mandatory party species. Beelzemon is defeated and contained; residents are not required to forgive him. His plan fails, and he does not reveal knowledge of Apocalymon that he never possessed.

**The final mandatory scene is back in File Town**, at the opening meal table. Botamon asks whether the party will return tomorrow. The answer is yes. Credits follow the return, not a boss explosion.

### Postgame — the harm left behind

Ancient Labyrinth remains a short records rescue. Kuramon’s surviving index shows negative data still converging despite the restored routes. Storybook Isles remains a low-level letter-carrier rescue; its forwarding record locates the concentration at the isolated summit. Only after BOTH postgame debriefs does an explicitly endgame dispatch open a separate **Apocalymon** encounter in the existing summit space. This is a proposed encounter variant, not a thirty-sixth zone or an ambush boss in a level-5 dungeon. Apocalymon embodies discarded suffering that Beelzemon never understood. Defeating it protects rescued lives rather than invalidating the main ending. Return to File Town for a survivor debrief, then resume ordinary help. Repeats use new requests, never the same resident kidnapped again.

## Every released zone: missions, gates and returns

`M` main, `O` optional, `P` postgame, `H` hub. Prerequisites are completed camp debriefs; **AND** means both/all. Camp access is included where needed. The table is topologically ordered: no mandatory or optional circular gates. Optional branches never gate the main ending. All proposed place names predate the crisis; clients refer to familiar geography rather than naming roads after current missions. Current names below are zone display names; localized/hidden branch names may differ.

| Role / current ID and name → proposed title | Departure / prerequisite | Mission and resolution | Return/debrief and consequence |
|---|---|---|---|
| H `guildmaster_island` — Guildmaster Island → File Island Settlements | New game | Hub container, not a conventional dungeon. Establish rescue cooperative and optional Monzaemon storehouse scene after Tropical. | Camp services and local encounter return scenes live here. Monzaemon challenge never blocks the main path. |
| M `tropical_path` — Tropical Path → Tropical Jungle | File Town / opening | Rescue Falcomon and sheltered Botamon/Punimon; existing endpoint clears their way out. Preserve the first dungeon's Baby/In-Training intent. | Introduce Native Forest, return File Town. Falcomon admits fear for the Babies kept him repeating an easy route. Guardromon descends Infinity Mountain and reports Beelzemon seized the summit Return Protocol; motive unknown. Forest access, Faded, Bramble, Tiny and Faultline open. |
| O `tiny_tunnel` — Tiny Tunnel → Underroot Tunnel | Native Forest / Tropical | Find Nyaromon with stranded Wanyamon; its scratched map identifies the exit during the rescue scene. | Native Forest family reunion. Optional Geode hint, never its only unlock. |
| M `faded_trail` — Faded Trail → Native Forest Trail | Native Forest / Tropical | Recover Lopmon and the undelivered return-mail register from disappearing markers. | Return Native Forest; Terriermon reads names. Contact Panorama and open safe travel, Fertile and Flyaway. No secret exit required. |
| O `bramble_woods` — Bramble Woods → Bramble Grove | Native Forest / Tropical | Rescue Palmon's food convoy after barriers redirected it into thorns. | Return Native Forest with supplies; open Sickly Hollow. |
| M `faultline_ridge` — Faultline Ridge → Drill Tunnel | File Town / Tropical and Forest access | Rescue Gotsumon surveyors through the established lower-floor tunnel network. Their route seals reset at each attempted exit; reconnect Drill Tunnel and expose passage toward Signpost Forest. | Return File Town; report sent to Native Forest. Open Trickster Woods as previously requested. |
| M `trickster_woods` — Trickster Woods → Signpost Forest | Native Forest / Faultline | Impmon's misleading signs shelter travelers from patrols. Defeat the patrol and recover a routing plate; it admits its warnings were terrible. | Return Native Forest; confirm shared fault. Open Overgrown and Moonlit; this main revelation is also required before Great Canyon travel. |
| O `overgrown_wilds` — Overgrown Wilds → Misty Trees | Native Forest / Trickster | Rescue Woodmon maintenance crew at an overgrown communication relay. | Return Native Forest; nursery check-ins resume in a scene, no power-management mechanic. |
| O `moonlit_courtyard` — Moonlit Courtyard → Moonlit Court | Native Forest / Trickster | Bakemon works at night to avoid frightening clients. Rescue its sorter and archive sack. | Return Native Forest; postal staff offer a daylight desk. Open Secret Garden. |
| O `sickly_hollow` — Sickly Hollow → Geko Hollow | Native Forest / Bramble | Rescue Betamon technician and its notes explaining contaminated runoff. | Return Native Forest; boil water and reroute supply in a scene. Later reservoir dialogue acknowledges it; no main gate. |
| O `secret_garden` — Secret Garden → Village Garden | Native Forest / Moonlit | Pabumon caretakers hide residents with incomplete records. Calm a frightened defender through the endpoint encounter and establish a safe return list. | Return Native Forest; refuge opens. No free recruits or requirement to kill nursery residents. Existing challenge variants remain optional. |
| M `fertile_valley` — Fertile Valley → Gear Savanna | Panorama / Faded | Rescue Armadillomon carriers and seed stores stranded on the supply route. | Return Panorama; provision the next expedition. Great Canyon requires this AND Flyaway AND Trickster. |
| M `flyaway_cliffs` — Flyaway Cliffs → Panorama Cliffs | Panorama / Faded | Rescue Hawkmon scouts circling under contradictory safe-route orders. | Return Panorama. With Fertile and Trickster, open Great Canyon travel; open Panorama optional dispatches. |
| O `training_maze` — Training Maze → Green Gym Maze | Panorama training contact / Flyaway | Hawkmon's practice crew lost its marked return route. Finish the existing challenge and bring the group back in a scene. | Return Panorama; voluntary drills stay repeatable. No training prerequisite for story. |
| O `wayward_wetlands` — Wayward Wetlands → Geko Wetlands | Panorama / Flyaway | Rescue Otamamon workers marooned by flood diversion and recover their survey. | Return Panorama; couriers issue warnings. Repeats are new seasonal requests. |
| O `geode_crevice` — Geode Crevice → Crystal Crevice | Panorama / Flyaway; Tiny adds a hint only | Rescue prospectors who followed an echo instead of their beacon. Identify the mistaken signal in the endpoint scene. | Return Panorama; markers are corrected. No sound puzzle or rare crystal gate. |
| O `lava_floe_island` — Lava Floe Island → Lava Anchorage | Panorama expedition contact / Flyaway | Rescue Meramon lighthouse crew stranded when cooling deliveries stopped. | Return Panorama by dispatch boat. Open Castaway; do not add a Base entrance. |
| O `castaway_cave` — Castaway Cave → Coela Cavern | Panorama expedition contact / Lava Floe | Distress bottles have different dates; rescue the still-living Coelamon keeper instead of assuming all calls are stale. | Return Panorama; Falcomon separates mail for living recipients from archive records. |
| M `copper_quarry` — Copper Quarry → Factorial Quarry | Great Canyon / Trickster AND Fertile AND Flyaway | Rescue Mamemon's ToyAgumon apprentice and recover maintenance records from a sealed vault. Controlled opening is a scene. | Return Great Canyon workshop; records prove forged routing commands came from the occupied summit. With Depleted, open Misty travel. Beelzemon, not Guardromon, authored the malicious changes. |
| M `depleted_basin` — Depleted Basin → Great Canyon Basin | Great Canyon / Trickster AND Fertile AND Flyaway | Rescue Tankmon and the water-train crew behind an automated closure. Tankmon saw Leviamon rise from the depths and fly toward Infinity Mountain; this authored sighting is part of this adaptation, not a canon claim. | Return Great Canyon; restore water. Tankmon describes Leviamon, the first confirmed awakened accomplice. Guardromon links sustained fear and anger to six dormant Demon Lords, but cannot yet name all six. With Copper Quarry, open Misty and its main jobs; local investigations open. |
| O `forsaken_desert` — Forsaken Desert → Ancient Sands | Great Canyon / Depleted | Starmon misread a recall order and left its caravan. Rescue the caravan; it helps carry supplies. | Return Great Canyon; public apology and ordinary water-delivery shift, not an automatic villain role. |
| O `relic_tower` — Relic Tower → Overdell Tower | Great Canyon / Copper Quarry | Rescue Hagurumon's records keeper beneath obsolete safety machinery; recover original charter. | Return Great Canyon. Original charter proves the Return Protocol once returned travelers safely; a defaced register hints at six awakening sites. Optional enrichment; mandatory debriefs repeat essential clues. |
| O `sleeping_caldera` — Sleeping Caldera → Lava Caldera | Great Canyon / Depleted | Rescue night workers while Meramon and Frigimon leads argue about a failed heat exchange. | Return Great Canyon; leads sign one repair schedule and shelter heat resumes. No engineering minigame. |
| O `ambush_forest` — Ambush Forest → Bamboo Thicket | Native Forest / Depleted; Great Canyon sends request | Goblimon transporters diverted supplies to stranded nursery residents. Rescue transporters and injured accuser. | Return Native Forest; restitution and shared delivery roster settle it. No new Great Canyon-local entrance. |
| O `eon_island` — Eon Island → Eon Island | Native Forest archive contact / Copper Quarry | Rescue Elecmon custodian from an obsolete beacon still attracting volunteer teams. | Return Native Forest; label old relay and add dates to records. Open Prism. Keep existing low-level short excursion. |
| O `prism_isles` — Prism Isles → Prism Isles | Native Forest archive contact / Eon | Rescue Salamon surveyors with conflicting safe-route observations; assemble reports in a scene. | Return Native Forest; disagreement becomes evidence rather than blame. No new color-switch mechanic. |
| O `cave_of_whispers` — Cave of Whispers → Whispering Cave | Misty / Copper Quarry AND Depleted | Wizardmon follows a call dismissed as a recording. Rescue a living DemiDevimon operator beneath the loop. | Return Misty; remove one name from the missing list. Existing gentle level range is a recovery mission, not a main difficulty gate. |
| M `thunderstruck_pass` — Thunderstruck Pass → Thunder Pass | Misty / Copper Quarry AND Depleted | Rescue Aquilamon and the grounded courier crew. Daemon incites accusations while Barbamon withholds their route permits for tribute. Two sequential endpoint encounters free the crew and the manual message route. | Return Misty; Aquilamon admits fear of blame made it hoard reports. Crew testimony names Daemon and Barbamon and explains the anger/greed harvest. With Veiled, open Snowbound. |
| M `veiled_ridge` — Veiled Ridge → Misty Ridge | Misty / Copper Quarry AND Depleted | Rescue Renamon scouts drawn into Lilithmon’s promises that everyone else will abandon them. Defeat Lilithmon at the endpoint and retrieve the genuine summit authorization. | Return Misty; Renamon describes whispered mistrust and identifies Lilithmon. Wizardmon compares both main rescue reports to explain emotion harvesting. With Thunderstruck, open Snowbound. |
| M `snowbound_path` — Snowbound Path → Freezeland Path | Misty / Thunderstruck AND Veiled | Rescue the final supply team from Belphemon Rage Mode, awakened beneath the snow by accumulated resentment and exhaustion. Defeat it to clear the supply approach; aid is a narrative flag, not an inventory quota. | Introduce Freezeland, return Misty to confirm arrival. Survivors name Belphemon Rage Mode and recognize deliberate awakening, not bad weather. Open safe Freezeland travel and Champion’s Road. |
| O `treacherous_mountain` — Treacherous Mountain → Ice Mountain | Misty / Snowbound; Freezeland issues request | Rescue Triceramon weather observer, a mission visitor, from the failed watch post. | Return Misty; send forecast to Freezeland. Alters preparation dialogue, not success odds or ending requirements. |
| M `champions_road` — Champion's Road → Infinity Approach | Freezeland / Snowbound | Rescue a stranded advance party from Leviamon and then Lucemon Chaos Mode at separate endpoint beats. Lucemon offers a perfect world with no choices; the party refuses and opens the summit approach. | Return Freezeland with the advance party. All six accomplices are now identified and confronted. Guardromon and Unimon’s recovered instructions explain how to isolate the Return Protocol; prepare the finale at the kitchen table. Do not require unreleased the_sky. |
| M `guildmaster_trail` — Guildmaster Trail → Infinity Mountain | File Town / visible at opening; finale job after Champion's Road | The established Infinity Mountain ascent is guarded by Beelzemon. Rescue Unimon and beacon workers, defeat Beelzemon at the summit, and let the workers isolate his alterations through the manual release. | Return File Town for meal and credits. Reconnected routes and local check-ins let the restored emergency system serve residents again. Beelzemon’s fate remains supervised custody, without demanding instant forgiveness. Open archive aftermath and the optional Apocalymon investigation; retain optional jobs. |
| P `labyrinth_of_the_lost` — Labyrinth of the Lost → Ancient Labyrinth | Great Canyon archive contact / finale | Rescue Kuramon archivist and incomplete name index. Beneath the ordinary missing-person records, discover discarded negative data still converging after Beelzemon’s defeat. | Return Great Canyon; preserve uncertain names rather than invent identities. Wizardmon and Guardromon identify Apocalymon’s emerging trace, a consequence Beelzemon did not anticipate. Open Storybook Isles investigation; this short low-level rescue is not the high-level boss arena. |
| P `the_neverending_tale` — The NeverEnding Tale → Storybook Isles | Great Canyon archive contact / Labyrinth | Rescue Bakemon’s replacement letter carrier and a forwarding record for a long-delayed message. The record locates Apocalymon’s condensation at the isolated Infinity Summit. | Return Great Canyon and deliver the letter through Falcomon. Unlock a separate, explicitly endgame Apocalymon summit dispatch using the existing summit encounter space; do not add the boss to this level-5 route. After that optional challenge, return File Town for a survivor debrief and ordinary rescue-board requests. |

## Progression and scene contract

Main chain, with joins explicit:

```text
Opening → Tropical → Faded → (Fertile AND Flyaway) ─┐
              └→ Faultline → Trickster ──────────┴→ (Copper Quarry AND Depleted)
                                                      ↓
                                          (Thunderstruck AND Veiled)
                                                      ↓
                               Snowbound → Champion's Road → Guildmaster → return/credits
```

Each mission receives five beats: client names the problem at camp; departure states the expected return camp; a short midpoint clue is optional/skippable on repeats; normal endpoint resolves the rescue; camp debrief shows an aftermath and posts the next job. Act scenes expand the debrief rather than interrupting every floor. Clearing a route reconnects its safe return corridor to the network; repeat dungeon expeditions still serve outlying residents and local hazards. Rescued residents never claim all loops ended before the summit restoration. The optional postgame chain is finale → Ancient Labyrinth → Storybook Isles → separate Apocalymon summit dispatch → File Town return.

Future implementation should separate accepted/resolved/debriefed states. Endpoint sets resolved, camp scene sets debriefed and awards once. Crashes or scene skips must not strand unlocks or duplicate rewards. Species and team changes between beats remain valid. A lost mission never permanently removes its client.

Guildmaster Trail remains visible and playable early as requested. An early clear gets its ordinary challenge result: Beelzemon’s summit perimeter can be repelled, but his protocol chamber remains sealed until the rescue network is coordinated. Do not reveal all six awakenings or play the finale out of order. After Champion's Road, a recorded early clear should permit a **proposed camp dispatch to the existing summit/final encounter** for the rescue job, or a full replay by choice. Do not force a second long ascent merely for credits. This dispatch is future design work, not a currently verified shortcut. A final-encounter failure retries under normal rules and still returns home afterward.

Secret exits remain optional loot/challenge routes. No main clue depends on one random floor or rare item. Current scripts refer to unreleased `deserted_fortress`, `barren_tundra`, and `the_sky`; none gates this story. Current forward transitions (including Tiny Tunnel) and old blanket-unlock saves need a later migration review. Offer missing debrief recaps for already completed routes rather than silently resetting saves. Do not introduce any story gates into the present ability/move build.

## Encounter and replay direction

Named clients are authored replacements, not an instruction to replace every wild spawn with one species. Retain appropriate local elements and low-level balancing. Small expert workers, strong exhausted caregivers, Virus clients and gentle Goblimon vary the cast. Forest security can use ToyAgumon/Hagurumon; coastal teams Gomamon/Betamon; ravine crews Gotsumon/Hagurumon; cold-region teams Frigimon/Unimon. NPC role matters more than stage or alignment.

Defeat still awards scans under existing rules. Story text describes retreats/disrupted patrols; avoid saying the party killed a named rescue target and then casually employing it. Named Demon Lord bosses above are design assignments; their encounter scripts and tuning remain future work. Two-boss routes use sequential encounters and preparation opportunities, never an unannounced simultaneous double boss. Avoid stage/attribute requirements and tune to the existing route difficulty. Repeated clears use fresh requests, surveys, repairs and delivery text, not repeated first-rescue scenes or rewards.

## Coverage and handoff

Inventory source: `Released: true` in actual `DumpAsset/Data/Zone/*.json`, cross-checked with `DataAsset/Digimon/dungeon_audit.json`. Camp baseline: `docs/DIGIMON_DUNGEON_PROGRESS.md` and ground entry lists; transitions inspected in zone callbacks. Companion `storyboard_routes.json` records all 35 IDs, current names, proposed names, camps, prerequisites and a valid order. It is documentation with no runtime consumer.

Before story implementation: bind role-based residents to real map entities; validate seven proposed optional dispatches; reconcile returns and early-clear summit handling; then implement one complete request-to-return chapter and playtest it before expanding. This deliverable stops at a complete storyboard through all released routes, finale, and aftermath. Dialogue drafts below are documentation only; no runtime dialogue, assets or code have been changed.


## Naming reference and adaptation

The requested [File Island reference](https://digimon.fandom.com/wiki/File_Island) supplies geographic inspiration: File City, Native Forest, Gear Savanna, Drill Tunnel and Freezeland. Its direct page fetch was unavailable; its indexed location text and [Wikimon’s File Island listing](https://wikimon.net/File_Island) were used to check these names. Our layout remains PMDO’s existing topology, not a claim to reproduce a canonical island map. File Town, Panorama Camp, Great Canyon Camp, Misty Shelter and Freezeland Camp are long-established settlements. Guildmaster Trail becomes Infinity Mountain and Summit Camp becomes Infinity Summit. Drill Tunnel and Signpost Forest follow the requested mapping. Other names describe terrain or existing landmarks; none commemorates Beelzemon’s current crisis.

## Resident dialogue states — authored drafts

Each row is one named resident or an explicitly named spokesperson for a rescued group. These are the complete speaking rescue cast for this draft; unnamed group members use ambient reactions and do not silently create missing dialogue obligations. “Before” plays at first camp contact, or at the first trapped encounter for residents not yet reachable in camp. “After” replaces their camp conversation only after that resident’s rescue and route debrief (not merely arriving at the next camp). A distressed resident remains distressed on repeat visits until that flag is set. Service menus remain usable. Characters can be grateful without becoming perfectly healed; no rewards require choosing a therapeutic response.

| Resident / associated request | Before rescue or reconnection | After rescue and camp debrief |
|---|---|---|
| Clockmon / File Town opening, Tropical | “If I miss one more check-in, someone will not come home. Give me a moment. I have to count again.” | “You returned when you said you would. I will post what we know, and admit what we do not.” |
| Guardromon / arrives after Tropical; finale follow-through | “Beelzemon took the station. I tried every route down. I should have stopped him before any of this happened.” | “You restored the route I could not. I can explain the controls now. I will help bring the others back.” |
| Falcomon / Tropical | “The little ones cannot survive a wrong turn! No, we stay here. Just until I am certain.” | “It was an easy path. I made every turn impossible in my head. Thank you for bringing all of us home.” |
| Botamon / Tropical | “Every tree looks like the last one. Please do not leave without us.” | “You came back! Will you come back tomorrow, too?” |
| Punimon / Tropical | “I cannot sleep. What if everyone goes while my eyes are shut?” | “Falcomon knows we are here. I think I can sleep now.” |
| Monzaemon / Forest storehouse relief | “I held that shutter all night. Now everyone wants something else. Let me sleep. Someone else can save them.” | “I was tired, then I stopped letting anyone help. Thank you for taking a shift. The storehouse is yours to use.” |
| Sunflowmon / Forest nursery, Tropical | “Beds, meals, missing names… Do not tell me to rest while a child is outside.” | “There are more hands here now. I can leave the list with someone and sit with the children.” |
| Gatomon / Tiny Tunnel | “Someone let Nyaromon wander. Was it you? Nobody tells me anything!” | “You brought my child home. I accused everyone because I was frightened. I owe them more than excuses.” |
| Nyaromon / Tiny Tunnel | “I made a map, but grown-ups never listen. Maybe I drew everything wrong.” | “You used my map! I will show it to the other little ones before we go out again.” |
| Wanyamon / Tiny Tunnel | “If Nyaromon leaves, I will be alone. Please say we can stay together.” | “We both made it. Next time we will tell someone where we are going.” |
| Lopmon / Faded Trail | “The address might be wrong. I cannot deliver a letter to the wrong family. I have to start again.” | “I checked forever and delivered nothing. We can ask at the next camp instead of pretending to know.” |
| Terriermon / Faded Trail debrief | “Lopmon is fine! Everything is fine! Stop asking me where it is.” | “I did not know. I should have said that. Thank you for giving us a real answer.” |
| Palmon / Bramble convoy | “We counted every ration. If I share one now, what happens tomorrow?” | “The pantry has a route again. I will stop treating every hungry neighbor like a thief.” |
| Gotsumon surveyor Flint / Drill Tunnel | “We cut this passage ourselves! I refuse to ask some strangers how to leave it.” | “The seals changed, and I was too proud to say I was lost. Let me mark the safe passage for you.” |
| Impmon / Signpost Forest | “Laugh at my signs and see if I help you! The patrol follows the proper ones.” | “I kept people hidden, but frightened the rescuers away too. I will mark the real exit with you.” |
| Woodmon foreman Bark / Overgrown | “Nobody touches this relay but me. Last time someone helped, everything broke.” | “You got the crew out. I can show another worker the controls instead of guarding them forever.” |
| Bakemon postal sorter Veil / Moonlit | “They will scream if they see me. Leave the sack and go. I work better alone.” | “A daylight desk? With my name on it? I would like to try.” |
| Betamon / Sickly Hollow | “If the water is bad, they will blame me. I cannot bring these notes back.” | “The notes helped them fix it. Hiding them would have hurt everyone. Thank you for coming.” |
| Pabumon caretaker Dew / Secret Garden | “Their records are missing. If officials see them, they might take them away. Nobody comes in.” | “You wrote down who needs help, not who deserves it. We can open the gate.” |
| Armadillomon carrier Tread / Fertile | “The seeds are worth more than one tired carrier. I will not leave them.” | “You brought both home. Next time I will call for help before I cannot stand.” |
| Hawkmon / Flyaway | “I am not a hatchling. I can find the route alone. Stop following me!” | “I was scared you would see me fail. I would rather fly with a crew than disappear proving a point.” |
| Hawkmon practice leader Pinion / Training Maze | “It is only practice. If we admit we are lost, they will never trust us.” | “We can mark a return route and ask someone to check it. That is practice too.” |
| Otamamon foreman Reed / Wetlands | “The other crew opened that channel on purpose. Let them come fix it!” | “They were stranded too. We will compare surveys before we start shouting.” |
| Gotsumon prospector Quartz / Geode | “I heard the beacon. I know I heard it. Do not make me admit I led them wrong.” | “An echo fooled me. Your marker will keep the next crew from following my mistake.” |
| Meramon keeper Wick / Lava Floe | “If the light goes out, every wreck is my fault. I cannot leave this platform.” | “The relief crew knows the way now. I can go home without abandoning the light.” |
| Coelamon / Castaway | “I sent so many bottles. Perhaps nobody wants another one. Perhaps I should stop.” | “You read the dates and came for me. I still have someone to write to.” |
| ToyAgumon apprentice Chip / Copper Quarry | “Mamemon will see the broken lock and know I ruined it. I can fix it before anyone comes.” | “You saved me and the log. I will tell Mamemon what happened, even the part I am ashamed of.” |
| Mamemon / Copper Quarry | “One apprentice missing. One charge unaccounted for. Do not touch anything—I cannot lose anyone else.” | “Chip is home. We will inspect the damage together. A careful repair starts with an honest report.” |
| Tankmon / Depleted | “The crew needs water. I saw something enormous rise below us, but if I stop hauling, everyone suffers.” | “Leviamon came out of the depths and flew toward Infinity Mountain. I should have reported it sooner. You brought the crew back; I can speak now.” |
| Starmon / Forsaken | “I followed the recall exactly. It cannot be my fault the caravan is still out there.” | “Orders did not make them safe. I will apologize, then take the next water shift.” |
| Hagurumon archivist Ledger / Relic | “If a page is missing, I cannot certify any of it. We must keep searching.” | “We recovered enough to help. I will label the gaps instead of locking the whole archive.” |
| Hagurumon workshop keeper Tally / Copper Quarry | “The records disagree. I will not sign off on a single repair until someone admits who changed them.” | “The forged commands came from the summit. We can repair the pumps while the archivists trace the rest.” |
| Meramon heat lead Kiln / Sleeping Caldera | “Frigimon keeps undoing my work! I will not sign another shared plan.” | “We were both protecting the workers badly. One schedule, checked by both of us.” |
| Frigimon cooling lead Rime / Sleeping Caldera | “Meramon never listens. If I leave my station, it will overheat everything.” | “The workers are home. I can hand over a shift without treating it like surrender.” |
| Goblimon convoy leader Moss / Ambush | “Everyone is frightened. Sit down first; then we can work out who needs the supplies.” | “Good. Both groups are home. Let us put both names on the next delivery list.” |
| Goblimon accuser Thorn / Ambush | “They took our supplies! Do not ask why. Just bring them back!” | “The nursery needed them too. I was hurt and wanted someone to blame. We can share the route.” |
| Elecmon / Eon | “This beacon was my duty. If it is obsolete, what was I keeping watch for?” | “You found a use for the records. I can help with the new dates instead of guarding an empty pier.” |
| Salamon survey lead Iris / Prism | “Their report disagrees with mine. Someone must be lying, and it is not me.” | “The route changed between our visits. We needed both reports. I should have listened.” |
| DemiDevimon operator Echo / Cave of Whispers | “They call every message a recording. Why should I waste another breath?” | “You answered. I will put my name and the time on the next call.” |
| Wizardmon / Cave and main Misty debriefs | “One of these calls may still be alive. I cannot stop listening, even for a moment.” | “We can share the watch and check the dates. I do not have to hear every voice alone.” |
| Gotsumon rest keeper Slate / Cave of Whispers | “Another missing name. Another rescue promised. Why should I believe this one?” | “The operator is here, alive. I will make room on the board for returns, not only losses.” |
| Aquilamon / Thunderstruck | “If I admit we are grounded, every late rescue becomes my fault. Keep the reports here.” | “Daemon wanted us angry; Barbamon wanted our permits. Hiding the reports helped them. Take copies to every camp.” |
| Renamon scout Sable / Veiled | “Lilithmon said they would leave us behind. Tell me why I should believe you instead.” | “You came through the ridge for us. I will warn the other scouts about her promises.” |
| Frigimon shelter chief Hearth / Snowbound | “No more arrivals. We have no room, no fuel—no, do not look at the empty beds.” | “I was afraid of failing one more guest. The supplies arrived. Help me make up those beds.” |
| Gomamon supply leader Brine / Snowbound | “Belphemon is awake. We cannot move, and we cannot carry everything. I cannot choose what to leave.” | “You chose to bring us home first. We can recover supplies later. Tell the shelter we are coming.” |
| Triceramon / Treacherous | “I can withstand this weather. If I retreat, all those forecasts were worth nothing.” | “A warning from someone alive is worth more than a frozen instrument. I will send the forecast from camp.” |
| Gotsumon advance leader Cairn / Champion’s Road | “Leviamon is ahead. Lucemon says surrender is the only safe choice. I cannot tell the others we are trapped.” | “You broke their hold. I can tell the crew the truth and still lead them home.” |
| Unimon / Guildmaster summit | “The release might work. Might. I cannot send the workers toward another mistake.” | “They reached it together. Guardromon can rebuild the checks with us. Thank you for giving us a way down.” |
| Hagurumon beacon technician Relay / Guildmaster summit | “If Beelzemon sees one switch move, it is over. We should wait. We should keep waiting.” | “You held the approach while we isolated the commands. I want to see the town before my next shift.” |
| Kuramon / Labyrinth postgame | “So many missing names. If I cannot restore all of them, why save this fragment?” | “The fragment led us to people who still need help. We will mark the unknown names with care.” |
| Bakemon letter carrier Postscript / NeverEnding Tale | “It is so late that delivering it may hurt more than losing it. Perhaps I should stay.” | “They wanted to know someone remembered. I will ask before deciding for them next time.” |

Local residents without a dungeon rescue still have a reconnection pair: Gomamon the File Town planner says “Every crossing comes back here; I cannot promise a route” / “Your first return gives us a route we can plan around” after Tropical; ToyAgumon the repair apprentice Bolt says “Everything I mend breaks again” / “This bench stayed fixed long enough for someone to come home” after Tropical; calm Goblimon queue steward Fern says “One name at a time; I am listening” / “One less missing name today; who is next?” after Tropical; Chuumon the quartermaster says “If I open another crate, we might run out” / “The supply route is open; I can count what arrives as well as what leaves” after Fertile; Armadillomon stores keeper Shell says “I have checked that shelf six times” / “I can let the next shift check it” after Fertile; Renamon roster keeper Reed says “An empty slot feels like a promise I broke” / “I can put their return dates beside their names” after Tropical. These are separate individuals from same-species rescue clients.

The two-stage dialogue contract covers each named resident; group rescues receive their spokesperson’s pair plus a visible returned group. Finale and Apocalymon debriefs add shared hope without overwriting unresolved optional residents’ state. No conversation changes or dialogue flags are implemented in the current build.
