using System;
using System.IO;
using System.Collections.Generic;
using RogueEssence;
using RogueEssence.Data;
using RogueEssence.Dungeon;
using RogueEssence.LevelGen;
using RogueEssence.Script;
using PMDC.Data;
using PMDC.Dungeon;

namespace DataGenerator
{
    // Uses the real serializer, indices and map generator without writing a player save.
    internal static class DigimonRuntimeChecks
    {
        // Character.Promote consults the current scene even outside a live battle.
        internal sealed class CheckScene : BaseScene
        {
            public override void Begin() { }
            public override void Exit() { }
            public override IEnumerator<YieldInstruction> ProcessInput() { yield break; }
            public override void Draw(Microsoft.Xna.Framework.Graphics.SpriteBatch batch) { }
        }
        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidDataException(message);
        }

        public static void Run()
        {
            LuaEngine.InitInstance();
            DataManager.InitInstance();
            DataManager.Instance.InitData();
            LuaEngine.Instance.LoadScripts();
            DataManager.Instance.SetProgress(new MainProgress(1, "digimon-runtime-check"));
            Require(DigimonExperience.Award(72, 8, 8) == 122, "Incorrect Digimon EXP formula");
            Require(DigimonExperience.Award(72, 8, 14) == 61, "Incorrect overlevel penalty");
            Require(DigimonExperience.Award(72, 8, 23) == 0, "Intro farming remains effective");
            string[] rewardStages = { "digi_baby", "digi_in_training", "digi_rookie", "digi_champion", "digi_ultimate", "digi_mega" };
            int[] expectedRewards = { 200, 200, 150, 100, 75, 50 };
            for (int i = 0; i < rewardStages.Length; i++)
            {
                Require(DigimonExperience.Award(100, 1, 1, rewardStages[i]) == expectedRewards[i], "Incorrect recipient-stage reward: " + rewardStages[i]);
                Require(DigimonExperience.Award(100, 1, 7, rewardStages[i]) == expectedRewards[i] / 2, "Stage reward bypasses overlevel penalty");
                Require(DigimonExperience.Award(100, 1, 16, rewardStages[i]) == 0, "Stage reward bypasses farming cutoff");
            }
            Require(DigimonExperience.Award(1, 1, 1, "digi_ultimate") == 0, "Fractional EXP must round down");
            int forms = 0;
            int familyBoxes = 0;
            int starterForms = 0;
            var syncPassive = (NLua.LuaFunction)LuaEngine.Instance.RunString("return require('origin.digimon.passive_abilities').sync")[0];
            foreach (string path in Directory.GetFiles(PathMod.ModPath("Data/Monster/"), "*.json"))
            {
                string id = Path.GetFileNameWithoutExtension(path);
                var monster = DataManager.Instance.GetMonster(id);
                if (!(monster.Forms[0] is DigimonFormData form)) continue;
                forms++;
                Require(DataManager.Instance.GetGrowth(monster.EXPTable).GetExpToNext(5) > 0, id + ": missing stage EXP curve");
                Require(form.LevelStats.Count == 99, id + ": missing level curve");
                Require(form.SummaryAttribute == "Virus" || form.SummaryAttribute == "Vaccine" || form.SummaryAttribute == "Data" || form.SummaryAttribute == "Free", id + ": missing Digimon attribute");
                Require(form.Family_Types != null && form.Family_Types.Count > 0 && form.Family_Types.TrueForAll(t => !String.IsNullOrWhiteSpace(t) && t != "NO DATA")
                    && form.Family_Types.Count == new HashSet<string>(form.Family_Types).Count, id + ": missing or invalid Digimon family types");
                Require(!String.IsNullOrWhiteSpace(form.SummaryFamilyType), id + ": missing Digimon family type");
                Require(File.Exists(PathMod.ModPath("Content/StaticCreature/" + monster.IndexNum + ".png")), id + ": missing static art");
                for (int level = 1; level <= 99; level++)
                    Require(form.GetStat(level, Stat.HP, 0) > 0, id + ": invalid HP");
                foreach (var skill in form.LevelSkills)
                {
                    DataManager.Instance.DataIndices[DataManager.DataType.Skill].Get(skill.Skill);
                    Require(DataManager.Instance.GetSkill(skill.Skill) != null, id + ": invalid skill");
                }
                var team = new ExplorerTeam();
                var character = team.CreatePlayer(new RogueElements.ReRandom(1), new MonsterID(id, 0, "normal", Gender.Genderless), 5, "none", 0);
                Require(form.Intrinsic1.StartsWith("digi_"), id + ": missing Digimon passive");
                Require(DataManager.Instance.GetIntrinsic(form.Intrinsic1).Released, id + ": unreleased passive");
                syncPassive.Call(character);
                Require(character.BaseIntrinsics[0] == form.Intrinsic1, id + ": passive migration failed");
                Require(character.FormHistory.Count == 1 && character.FormHistory[0] == character.BaseForm, id + ": form history was not initialized");
                Require(!(bool)syncPassive.Call(character)[0], id + ": passive migration is not idempotent");
                if (form.LevelSkills[0].Skill.StartsWith("digi_starter_"))
                {
                    starterForms++;
                    var first = form.LevelSkills[0];
                    var move = DataManager.Instance.GetSkill(first.Skill);
                    Require(first.Level == 1 && move.BaseCharges == 20, id + ": invalid starter availability or PP");
                    Require(move.Data.SkillStates.GetWithDefault<BasePowerState>().Power == 20, id + ": invalid starter power");
                    for (int level = 1; level < 10; level++)
                        Require(form.RollLatestSkills(level, new List<string>()).Contains(first.Skill), id + ": starter lost before level 10");
                }
                character.Nickname = "Identity test";
                character.SaveLua();
                Require(character.Clone(new ExplorerTeam()).RewardIdentity == character.RewardIdentity, id + ": team snapshot changed identity");
                using (var stream = new MemoryStream())
                {
                    Serializer.SerializeData(stream, character);
                    stream.Position = 0;
                    var restored = (Character)Serializer.DeserializeData(stream);
                    Require(restored.RewardIdentity == character.RewardIdentity && restored.BaseForm.Species == id && restored.Nickname == character.Nickname
                        && restored.FormHistory.Count == 1 && restored.FormHistory[0] == character.BaseForm, id + ": save identity or lineage mismatch");
                }
            }
            Require(forms == 341, "Expected 341 Phase 2 forms, found " + forms);
            Require(starterForms == 68, "Expected 68 low-stage starter learnsets, found " + starterForms);
            // Execute native damage events, including a cloned conditional event.
            var agumonPassive = DataManager.Instance.GetIntrinsic("digi_agumon");
            var attackContext = new BattleContext(BattleActionType.Skill);
            attackContext.Data = new BattleData();
            attackContext.Data.ID = "digi_pepper_breath";
            attackContext.Data.Category = BattleData.SkillCategory.Magical;
            foreach (var effect in agumonPassive.OnActions.EnumerateInOrder())
            {
                var routine = ((BattleEvent)effect.Clone()).Apply(null, null, attackContext);
                while (routine.MoveNext()) { }
            }
            Require(attackContext.GetContextStateMult<DmgMult>().Multiply(100) == 110, "Agumon signature passive did not execute");
            var allyContext = new BattleContext(BattleActionType.Skill);
            allyContext.Data = new BattleData();
            allyContext.Data.Category = BattleData.SkillCategory.Physical;
            foreach (var effect in agumonPassive.ProximityEvent.OnActions.EnumerateInOrder())
            {
                var routine = effect.Apply(null, null, allyContext);
                while (routine.MoveNext()) { }
            }
            Require(allyContext.GetContextStateMult<DmgMult>().Multiply(100) == 104, "Agumon ally damage event did not execute");
            Require(((DeepBreathEvent)new DeepBreathEvent(true).Clone()).RestoreAll, "PP recovery clone lost all-moves setting");
            Require(((TargetNeededEvent)new TargetNeededEvent(Alignment.Foe).Clone()).Target == Alignment.Foe, "Enemy filter clone lost alignment");
            var retentionTeam = new ExplorerTeam();
            var retentionCharacter = retentionTeam.CreatePlayer(new RogueElements.ReRandom(1), new MonsterID("agumon", 0, "normal", Gender.Genderless), 65, "none", 0);
            var retentionCheck = (NLua.LuaFunction)LuaEngine.Instance.RunString(@"
return function(c)
  local P = require('origin.digimon.progression')
  local R = require('origin.digimon.runtime_catalog')
  SV.Digimon = require('origin.digimon.scan_ledger').new()
  local previousHub, previousRespawn = P.hub, COMMON.RespawnAllies
  P.hub = function() return true end
  COMMON.RespawnAllies = function() end
  local ok, err = pcall(function()
    local row = P.progress(c)
    c.AtkBonus = 25
    local form = _DATA:GetMonster('agumon').Forms[0]
    local expected = math.floor((form:GetStat(65, RogueEssence.Data.Stat.Attack, 0) - form:GetStat(5, RogueEssence.Data.Stat.Attack, 0) + 25)/5)
    local function change(target)
      for _,e in ipairs(R.transitions) do
        if e.from==c.BaseForm.Species and e.to==target then
          assert(P.change(c,e))
          assert(c.BaseIntrinsics[0]==_DATA:GetMonster(target).Forms[0].Intrinsic1, 'evolution did not replace passive')
          return
        end
      end
      error('missing edge')
    end
    change('koromon')
    assert(c.Level==1 and c.EXP==0 and c.AtkBonus==expected)
    assert(c.LuaDataTable.DigimonRetainedAtkBonus==expected)
    change('botamon')
    assert(c.AtkBonus==expected)
    c.Level=21
    change('koromon')
    assert(c.Level==1 and c.EXP==0 and c.AtkBonus>=expected)
  end)
  P.hub, COMMON.RespawnAllies = previousHub, previousRespawn
  assert(ok, tostring(err))
end")[0];
            retentionCheck.Call(retentionCharacter);
            Require(retentionCharacter.FormHistory.Count == 4
                && retentionCharacter.FormHistory[0].Species == "agumon"
                && retentionCharacter.FormHistory[1].Species == "koromon"
                && retentionCharacter.FormHistory[2].Species == "botamon"
                && retentionCharacter.FormHistory[3].Species == "koromon", "Form history did not retain the chronological Digivolution path");
            retentionCharacter.SaveLua();
            using (var stream = new MemoryStream())
            {
                Serializer.SerializeData(stream, retentionCharacter);
                stream.Position = 0;
                var loaded = (Character)Serializer.DeserializeData(stream);
                loaded.LoadLua();
                Require(Convert.ToInt32(loaded.LuaDataTable["DigimonRetainedAtkBonus"]) == retentionCharacter.AtkBonus, "Retained stats did not survive serialization");
                Require(loaded.FormHistory.Count == retentionCharacter.FormHistory.Count && loaded.FormHistory[3].Species == "koromon", "Form history did not survive serialization");
            }
            int attachmentCount = 0;
            foreach (string path in Directory.GetFiles(PathMod.ModPath("Data/Item/"), "digi_tm_*.json"))
            {
                string itemId = Path.GetFileNameWithoutExtension(path);
                var item = DataManager.Instance.GetItem(itemId);
                var skillId = item.ItemStates.GetWithDefault<ItemIDState>().ID;
                Require(item.Released && item.MaxStack == 1 && item.UsageType == ItemData.UseType.Learn, itemId + ": invalid consumable TM");
                Require(DataManager.Instance.GetSkill(skillId) != null, itemId + ": missing skill");
                foreach (string monsterPath in Directory.GetFiles(PathMod.ModPath("Data/Monster/"), "*.json"))
                {
                    var monster = DataManager.Instance.GetMonster(Path.GetFileNameWithoutExtension(monsterPath));
                    if (monster.Forms[0] is DigimonFormData)
                        Require(monster.Forms[0].CanLearnSkill(skillId), itemId + ": not teachable to " + monster.Name.DefaultText);
                }
                attachmentCount++;
            }
            Require(attachmentCount == 138, "Expected 138 common single-use TMs");
            int convertedItems = 0;
            foreach (string path in Directory.GetFiles(PathMod.ModPath("Data/Item/"), "*.json"))
            {
                string id = Path.GetFileNameWithoutExtension(path);
                var item = DataManager.Instance.GetItem(id);
                if (!(item.Comment ?? "").StartsWith("Cyber Sleuth equivalent.")) continue;
                DataManager.Instance.DataIndices[DataManager.DataType.Item].Get(id);
                Require(!String.IsNullOrEmpty(item.Name.DefaultText), id + ": missing converted item name");
                Require(!String.IsNullOrEmpty(item.Desc.DefaultText), id + ": missing converted item description");
                convertedItems++;
            }
            Require(convertedItems == 49, "Expected 49 converted item records, found " + convertedItems);
            int floorCount = 0;
            var dungeonIssues = new List<string>();
            void Check(bool condition, string message) { if (!condition) dungeonIssues.Add(message); }
            var releasedZones = new List<string>();
            foreach (string path in Directory.GetFiles(PathMod.ModPath("Data/Zone/"), "*.json"))
                if (DataManager.Instance.GetZone(Path.GetFileNameWithoutExtension(path)).Released)
                    releasedZones.Add(Path.GetFileNameWithoutExtension(path));
            releasedZones.Sort();
            string[] earlyZones = releasedZones.ToArray();
            foreach (string zoneId in earlyZones)
            {
                Console.WriteLine("Checking released zone: " + zoneId);
                var zoneData = DataManager.Instance.GetZone(zoneId);
                Check(zoneData.Released, zoneId + ": zone is not released");
                if (zoneId == "tropical_path") Check(zoneData.Segments.Count == 2, "Tropical Path secret room is missing");
                // Includes the exact Tropical Path seed reported by the player's crash log.
                ulong seed = zoneId == "tropical_path" ? 15908617376361912718UL : 42UL;
                var zone = zoneData.CreateActiveZone(seed, zoneId);
                int entryFloor = zoneId == "training_maze" ? 4 : 0;
                Check(zone.GetMap(new SegLoc(0, entryFloor)).EntryPoints.Count > 0, zoneId + ": menu entry is not playable");
                for (int segment = 0; segment < zone.Segments.Count; segment++)
                {
                    ZoneSegmentBase layout = zone.Segments[segment];
                    var floorIds = new List<int>(layout.GetFloorIDs());
                    if (floorIds.Count == 0 && layout.FloorCount < 0) floorIds.Add(0);
                    foreach (int floor in floorIds)
                    {
                        Map map = zone.GetMap(new SegLoc(segment, floor));
                        // Exercise the same fixed-map NPC conversion used when playing.
                        // This check uses an isolated save and restores the engine binding.
                        LuaEngine.Instance.RunString("_digimon_previous_zone = _ZONE; _ZONE = {CurrentZoneID='" + zoneId + "'}; SV.Digimon = require('origin.digimon.scan_ledger').new()");
                        try { LuaEngine.Instance.OnDungeonMapEnter(map.AssetName, map); }
                        finally { LuaEngine.Instance.RunString("_ZONE = _digimon_previous_zone; _digimon_previous_zone = nil"); }
                        bool randomEnemies = false;
                        IFloorGen generator = layout.GetMapGen(floor);
                        if (generator is GridFloorGen grid)
                            foreach (var step in grid.GenSteps.EnumerateInOrder())
                                if (step.GetType().Name.StartsWith("PlaceRandomMobsStep")) randomEnemies = true;
                        if (generator is RoomFloorGen rooms)
                            foreach (var step in rooms.GenSteps.EnumerateInOrder())
                                if (step.GetType().Name.StartsWith("PlaceRandomMobsStep")) randomEnemies = true;
                        string location = zoneId + " segment " + segment + " floor " + floor;
                        if (randomEnemies)
                        {
                            Check(map.TeamSpawns.CanPick, location + ": empty enemy respawn table");
                            Check(map.MapTeams.Count > 0, location + ": no initial enemies");
                            Check(map.ItemSpawns.CanPick, location + ": empty loot table");
                            Check(map.Items.Count > 0, location + ": no placed loot");
                        }
                        foreach (var item in map.ItemSpawns.EnumerateOutcomes())
                            Check(!item.ID.StartsWith("apricorn_") && DataManager.Instance.GetItem(item.ID).Released,
                                location + ": unavailable loot " + item.ID);
                        foreach (var item in map.Items)
                        {
                            if (item.IsMoney) continue;
                            var itemData = DataManager.Instance.GetItem(item.Value);
                            if (itemData.UsageType == ItemData.UseType.Box)
                                Check(!String.IsNullOrEmpty(item.HiddenValue), location + ": empty reward box " + item.Value);
                            if (itemData.UsageType == ItemData.UseType.Box && item.HiddenValue.StartsWith(DigimonFamilyItems.Prefix))
                                familyBoxes++;
                        }
                        Check(map.EntryPoints.Count > 0, zoneId + " segment " + segment + " floor " + floor + ": map generation fell back or has no entry");
                        for (int x = 0; x < map.Width; x++)
                            for (int y = 0; y < map.Height; y++)
                            {
                                var dest = map.Tiles[x][y].Effect.TileStates.GetWithDefault<DestState>();
                                if (dest == null || !dest.Dest.IsValid() || dest.Relative) continue;
                                // Relative stairs use out-of-range coordinates to exit the segment.
                                Check(dest.Dest.Segment < zone.Segments.Count, "Dangling stair segment");
                                if (dest.Dest.Segment >= zone.Segments.Count) continue;
                                ZoneSegmentBase target = zone.Segments[dest.Dest.Segment];
                                bool targetExists = target.FloorCount < 0;
                                foreach (int targetId in target.GetFloorIDs())
                                    if (targetId == dest.Dest.ID) targetExists = true;
                                Check(dest.Dest.ID >= 0 && targetExists, zoneId + " segment " + segment + " floor " + floor + ": dangling stair floor " + dest.Dest.ID);
                            }
                        int guardians = 0;
                        foreach (var team in map.MapTeams)
                            foreach (var character in team.Players)
                            {
                                if (character.LuaDataTable?["DigimonBoss"] is bool guardian && guardian) guardians++;
                                Check(DataManager.Instance.GetMonster(character.BaseForm.Species).Forms[0] is DigimonFormData, zoneId + ": non-Digimon encounter " + character.BaseForm.Species);
                            }
                        if (zoneId == "tropical_path" && segment == 0 && floor == 3) Check(guardians == 1, "Final floor needs exactly one guardian");
                        floorCount++;
                    }
                }
            }
            Require(dungeonIssues.Count == 0, string.Join("\n", dungeonIssues));
            Require(familyBoxes > 0, "No seeded treasure box held a Digimon family item");
            Console.WriteLine("Digimon runtime checks passed: " + forms + " forms; " + convertedItems + " converted items; " + earlyZones.Length + " released zones and " + floorCount + " seeded floors; " + familyBoxes + " treasure boxes holding family items; character save round trips.");
        }
    }
}
