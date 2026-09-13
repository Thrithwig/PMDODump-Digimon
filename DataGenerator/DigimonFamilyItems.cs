using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Newtonsoft.Json.Linq;
using RogueEssence;
using RogueEssence.Data;
using RogueEssence.Dungeon;
using RogueEssence.Script;
using PMDC.Data;
using PMDC.Dungeon;
using DataGenerator.Data;

namespace DataGenerator
{
    /// <summary>
    /// Builds the Digimon family-exclusive items from DataAsset/Digimon/family_items.json.
    /// Each row reuses a PMDO exclusive-item effect; eligibility is the family's member species,
    /// read from the installed Digimon forms, stored in the same FamilyState PMDO uses.
    /// Three-star items are swap-shop only and their recipes are written to Lua.
    /// </summary>
    internal static class DigimonFamilyItems
    {
        public const string Prefix = "digixcl_";
        private const string TradesPath = "Data/Script/origin/digimon/family_trades.lua";

        private static readonly (string from, string to)[] Wording =
        {
            ("Pokémon", "Digimon"), ("Pokemon", "Digimon"),
            ("Fairy-type", "Light-type"), ("Grass-type", "Plant-type"), ("Ground-type", "Earth-type"),
            ("Flying-type", "Wind-type"), ("Normal-type", "Neutral-type"),
        };

        public static void Run(string designPath)
        {
            LuaEngine.InitInstance();
            DataManager.InitInstance();
            DataManager.Instance.InitData();

            Dictionary<string, List<string>> members = LoadFamilies();
            JObject design = JObject.Parse(File.ReadAllText(designPath, Encoding.UTF8));

            HashSet<string> ids = new HashSet<string>();
            HashSet<string> names = new HashSet<string>();
            HashSet<string> covered = new HashSet<string>();
            List<(string item, string[] inputs)> trades = new List<(string, string[])>();
            int written = 0;

            foreach (JObject familyRow in design["families"])
            {
                string family = (string)familyRow["family"];
                if (!members.ContainsKey(family))
                    throw new InvalidDataException("Unknown Digimon family: " + family);
                if (!covered.Add(family))
                    throw new InvalidDataException("Family listed twice: " + family);
                string slug = Slug(family);
                Dictionary<int, List<string>> byTier = new Dictionary<int, List<string>> { { 1, new List<string>() }, { 2, new List<string>() }, { 3, new List<string>() } };

                int index = 0;
                foreach (JObject itemRow in familyRow["items"])
                {
                    index++;
                    string itemId = Prefix + slug + "_" + index.ToString("D2");
                    int tier = (int)itemRow["tier"];
                    string name = ((string)itemRow["name"]).Trim();
                    if (tier < 1 || tier > 3)
                        throw new InvalidDataException(itemId + ": tier must be 1, 2 or 3");
                    if (!ids.Add(itemId))
                        throw new InvalidDataException("Duplicate item id: " + itemId);
                    if (name == "" || !names.Add(name))
                        throw new InvalidDataException("Missing or duplicate item name: " + name);

                    ExclusiveItemEffect effect = (ExclusiveItemEffect)Enum.Parse(typeof(ExclusiveItemEffect), (string)itemRow["effect"]);
                    if (effect == ExclusiveItemEffect.None)
                        throw new InvalidDataException(itemId + ": effect None is not an item");
                    object[] args = BuildArgs(itemId, itemRow);

                    ItemData item = new ItemData();
                    item.UseEvent.Element = "none";
                    item.SortCategory = 17;
                    item.Name = new LocalText(name);
                    item.ItemStates.Set(new ExclusiveState(ExclusiveItemType.None));
                    item.ItemStates.Set(new FamilyState(members[family].ToArray()));
                    item.ItemStates.Set(new MaterialState());

                    List<LocalText> localArgs = new List<LocalText>();
                    AutoItemInfo.FillExclusiveEffects(itemId, item, localArgs, true, effect, args, false);
                    if (item.Name.DefaultText.StartsWith("**"))
                        throw new InvalidDataException(itemId + ": effect " + effect + " is marked incomplete by PMDO and cannot be used");
                    item.Desc = LocalText.FormatLocalText(item.Desc, localArgs.ToArray());
                    string text = item.Desc.DefaultText;
                    foreach ((string from, string to) in Wording)
                        text = text.Replace(from, to);
                    item.Desc = new LocalText("A rare treasure for " + family + " Digimon. " + text);

                    item.Rarity = tier;
                    item.Sprite = "Box_Yellow";
                    item.Icon = 10;
                    item.Price = 800 * tier;
                    item.UsageType = ItemData.UseType.Treasure;
                    item.BagEffect = true;
                    item.CannotDrop = true;
                    item.Comment = "Digimon family item: " + family + " tier " + tier;
                    item.Released = true;

                    DataManager.SaveEntryData(itemId, DataManager.DataType.Item.ToString(), item);
                    byTier[tier].Add(itemId);
                    written++;
                }

                foreach (int tier in new[] { 1, 2, 3 })
                {
                    if (byTier[tier].Count == 0)
                        throw new InvalidDataException(family + ": no tier " + tier + " item");
                }
                // Every three-star item is exchanged for the family's first one- and two-star items.
                foreach (string top in byTier[3])
                    trades.Add((top, new[] { byTier[1][0], byTier[2][0] }));
            }

            List<string> missing = new List<string>();
            foreach (string family in members.Keys)
            {
                if (!covered.Contains(family))
                    missing.Add(family);
            }
            if (missing.Count > 0)
                throw new InvalidDataException("Families without items: " + String.Join(", ", missing));

            WriteTrades(trades);
            Console.WriteLine(String.Format("Digimon family items: {0} families, {1} items, {2} swap recipes.", covered.Count, written, trades.Count));
        }

        private static Dictionary<string, List<string>> LoadFamilies()
        {
            Dictionary<string, List<string>> members = new Dictionary<string, List<string>>();
            foreach (string path in Directory.GetFiles(PathMod.ModPath("Data/Monster/"), "*.json"))
            {
                string id = Path.GetFileNameWithoutExtension(path);
                MonsterData monster = DataManager.Instance.GetMonster(id);
                if (!monster.Released || !(monster.Forms[0] is DigimonFormData form))
                    continue;
                foreach (string family in form.Family_Types)
                {
                    if (!members.ContainsKey(family))
                        members[family] = new List<string>();
                    members[family].Add(id);
                }
            }
            foreach (List<string> list in members.Values)
                list.Sort(StringComparer.Ordinal);
            return members;
        }

        /// <summary>Parameters in the same column order PMDO's exclusive-item sheet uses.</summary>
        private static object[] BuildArgs(string itemId, JObject row)
        {
            List<object> args = new List<object>();
            if (row["element"] != null)
                args.Add(RequireEntry(itemId, DataManager.DataType.Element, (string)row["element"]));
            if (row["status"] != null)
                args.Add(RequireEntry(itemId, DataManager.DataType.Status, (string)row["status"]));
            if (row["stat"] != null)
                args.Add(new Stat[] { (Stat)Enum.Parse(typeof(Stat), (string)row["stat"]) });
            if (row["target_element"] != null)
                args.Add(RequireEntry(itemId, DataManager.DataType.Element, (string)row["target_element"]));
            if (row["category"] != null)
                args.Add((BattleData.SkillCategory)Enum.Parse(typeof(BattleData.SkillCategory), (string)row["category"]));
            if (row["quantity"] != null)
                args.Add((int)row["quantity"]);
            if (row["map_status"] != null)
                args.Add(RequireEntry(itemId, DataManager.DataType.MapStatus, (string)row["map_status"]));
            return args.ToArray();
        }

        private static string RequireEntry(string itemId, DataManager.DataType type, string id)
        {
            try
            {
                DataManager.Instance.DataIndices[type].Get(id);
            }
            catch (Exception)
            {
                throw new InvalidDataException(itemId + ": unknown " + type + " '" + id + "'");
            }
            return id;
        }

        private static void WriteTrades(List<(string item, string[] inputs)> trades)
        {
            StringBuilder text = new StringBuilder();
            text.Append("-- Generated by DataGenerator -digimon-items from DataAsset/Digimon/family_items.json; do not edit.\n");
            text.Append("-- Each three-star family item is exchanged for that family's one- and two-star items.\n");
            text.Append("return {\n");
            foreach ((string item, string[] inputs) in trades)
            {
                List<string> quoted = new List<string>();
                foreach (string input in inputs)
                    quoted.Add("\"" + input + "\"");
                text.Append("  { Item=\"" + item + "\", ReqItem={" + String.Join(",", quoted) + "} },\n");
            }
            text.Append("}\n");
            string path = PathMod.ModPath(TradesPath);
            File.WriteAllText(path, text.ToString(), new UTF8Encoding(false));
        }

        private static string Slug(string family)
        {
            StringBuilder slug = new StringBuilder();
            foreach (char c in family.ToLowerInvariant())
            {
                if (Char.IsLetterOrDigit(c))
                    slug.Append(c);
                else if (c == ' ' || c == '-')
                    slug.Append('_');
            }
            return slug.ToString();
        }
    }
}
