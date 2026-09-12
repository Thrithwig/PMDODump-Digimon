# Reliable starter attacks

The derived `DataAsset/Digimon/starter_skills.json` assigns a level-1 elemental attack to all 67 Baby, In-Training and Rookie Digimon, plus Shoutmon under its existing Rookie progression policy. OmniShoutmon is excluded. The authoritative source CSV files, stage labels and original learned moves are unchanged.

All 16 generated attacks have power 20, 20 PP and 100 accuracy. Offensive category follows each species' source level-1 ATK versus INT: higher ATK selects Physical; higher INT or a tie selects Magic. Physical starters strike the adjacent enemy; special starters use the existing element-specific PMDO projectile presentation. Their descriptions state range and targeting. These are original dungeon adaptations, separate from source signature skills and common TMs.

The starter is the first level-1 learnset entry. The original source entries follow unchanged. Every affected species retains its starter in the engine's latest-four selection through levels 1–9, including ordinary level-5 Scan restoration. High-level restoration follows the existing latest-four policy; the starter remains relearnable.

Existing characters' current move slots are not overwritten. The Town (`base_camp_2`) move tutor can recall the new level-1 move under its normal rules. After an evolution/devolution into an eligible form, the Tree of Life uses the native level-1 learning prompts, letting the player choose whether to replace an occupied slot. Programmatic transitions remain free of UI yields.

Regenerate only this overlay with:

```powershell
python Scripts/digimon_starter_skills.py
```

The full `digimon_runtime_assets.py --phase2` generator also creates these attacks and applies the learnset overlay before the passive-ability overlay. Rebuild the Skill and Monster indexes after regeneration. No source move or TM is weakened to create these beginner options.
