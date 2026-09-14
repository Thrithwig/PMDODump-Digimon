using System;
using System.Collections.Generic;
using System.IO;
using PMDC.Data;
using PMDC.Dungeon;
using RogueEssence;
using RogueEssence.Data;
using RogueEssence.Dungeon;

namespace DataGenerator
{
    internal static class DigimonMatchupChecks
    {
        internal static void Run()
        {
            void Check(bool good, string message) { if (!good) throw new InvalidDataException(message); }
            string[] attributes = { "Virus", "Data", "Vaccine", "Free" };
            int[,] expected = { { 4, 6, 2, 4 }, { 2, 4, 6, 4 }, { 6, 2, 4, 4 }, { 4, 4, 4, 4 } };
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++)
                    Check(DigimonMatchups.AttributeMultiplier(attributes[i], attributes[j]) == expected[i, j], "Incorrect attribute matchup");
            Check(DigimonMatchups.AttributeMultiplier(null, "Virus") == 4, "Missing attribute must be neutral");
            Check(DigimonMatchups.AttributeMultiplier("Virus", "unknown") == 4, "Unknown attribute must be neutral");

            var table = DataManager.Instance.UniversalEvent.UniversalStates.GetWithDefault<ElementTableState>();
            var advantages = new HashSet<string> { "fire:grass", "grass:water", "water:fire", "electric:flying",
                "flying:ground", "ground:electric", "fairy:dark", "dark:fairy" };
            foreach (string attack in table.TypeMap.Keys)
                foreach (string defend in table.TypeMap.Keys)
                    Check(table.GetMatchup(attack, defend) == (advantages.Contains(attack + ":" + defend) ? PreTypeEvent.S_E : PreTypeEvent.NRM),
                        "Incorrect elemental matchup: " + attack + " -> " + defend);
            Check(PreTypeEvent.GetEffectivenessMult(PreTypeEvent.S_E_2) * 2 == PreTypeEvent.GetEffectivenessMult(PreTypeEvent.NRM_2) * 3,
                "Elemental advantage must be exactly 1.5x");

            var members = new Dictionary<string, Character>();
            var team = new ExplorerTeam();
            foreach (string path in Directory.GetFiles(PathMod.ModPath("Data/Monster/"), "*.json"))
            {
                string id = Path.GetFileNameWithoutExtension(path);
                if (DataManager.Instance.GetMonster(id).Forms[0] is DigimonFormData form && !members.ContainsKey(form.DigimonAttribute))
                    members[form.DigimonAttribute] = team.CreatePlayer(new RogueElements.ReRandom(1), new MonsterID(id, 0, "normal", Gender.Genderless), 5, "none", 0);
            }
            foreach (var category in new[] { BattleData.SkillCategory.Physical, BattleData.SkillCategory.Magical })
                for (int i = 0; i < 4; i++)
                    for (int j = 0; j < 4; j++)
                        foreach (string attack in table.TypeMap.Keys)
                            foreach (string defend in table.TypeMap.Keys)
                            {
                                var context = new BattleContext(BattleActionType.Skill) { User = members[attributes[i]], Target = members[attributes[j]], Data = new BattleData { Category = category } };
                                DigimonMatchups.ApplyAttribute(context);
                                int effectiveness = table.GetMatchup(attack, defend) + PreTypeEvent.NRM;
                                context.AddContextStateMult<DmgMult>(false, table.Effectiveness[effectiveness], table.Effectiveness[PreTypeEvent.NRM_2]);
                                int wanted = 100 * expected[i, j] * (advantages.Contains(attack + ":" + defend) ? 3 : 2) / 2;
                                Check(context.GetContextStateMult<DmgMult>().Multiply(400) == wanted, "Combined type/element scaling failed");
                            }
            Console.WriteLine("Cyber Sleuth matchup checks passed: all attribute/element pairs, physical/magical scaling, combined 2.25x advantage, neutral Wind vs Plant.");
        }
    }
}
