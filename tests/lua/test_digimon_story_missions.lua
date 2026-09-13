-- Exercise the authored primary-request state machine without the random board mod.
SV = {
  Digimon = { version = 1, species = {} },
  missions = { Missions = {}, FinishedMissions = {} },
  forest_camp = { ExpositionComplete = false }
}
local unlocked = {}
RogueEssence = {
  Dungeon = { MonsterID = function(id) return { Species = id } end },
  Data = { GameProgress = { ResultType = { Cleared = 1, Failed = 2 } } }
}
Gender = { Genderless = 0 }
GAME = {
  DungeonUnlocked = function(_, id) return unlocked[id] == true end,
  UnlockDungeon = function(_, id) unlocked[id] = true end
}
COMMON = {
  MISSION_INCOMPLETE = 0,
  SIDEQUEST_TYPE_RESCUE = 1,
  CreateMission = function(key, mission) SV.missions.Missions[key] = mission end,
  CompleteMission = function(key)
    SV.missions.FinishedMissions[key] = SV.missions.Missions[key]
    SV.missions.Missions[key] = nil
  end,
  UnlockWithFanfare = function(id) unlocked[id] = true end
}
UI = {
  SetSpeaker = function() end, WaitShowDialogue = function() end,
  ChoiceMenuYesNo = function() end, WaitForChoice = function() end,
  ChoiceResult = function() return true end
}

package.loaded['origin.digimon.story_missions'] = nil
local Story = require 'origin.digimon.story_missions'

-- Refusing the route clear, escaping it, and retrying never produce a debrief.
Story.interact('clockmon')
assert(SV.missions.Missions.DigimonStory_TropicalPath ~= nil)
assert(not Story.on_zone_exit('tropical_path', 0, RogueEssence.Data.GameProgress.ResultType.Cleared))
assert(Story.objective_met('DigimonStory_TropicalPath'))
assert(not Story.on_zone_exit('tropical_path', 0, RogueEssence.Data.GameProgress.ResultType.Failed))
assert(Story.on_zone_exit('tropical_path', 0, RogueEssence.Data.GameProgress.ResultType.Cleared))
Story.interact('clockmon')
assert(Story.debriefed('DigimonStory_TropicalPath'))
assert(unlocked.faultline_ridge and SV.missions.FinishedMissions.DigimonStory_TropicalPath ~= nil)

-- Forest Camp's first arrival is an independent prerequisite for the survey.
Story.interact('clockmon')
assert(SV.missions.Missions.DigimonStory_FaultlineRidge == nil)
SV.forest_camp.ExpositionComplete = true
Story.interact('clockmon')
assert(SV.missions.Missions.DigimonStory_FaultlineRidge ~= nil)
assert(Story.objective_met('DigimonStory_FaultlineRidge'))
assert(Story.on_zone_exit('faultline_ridge', 0, RogueEssence.Data.GameProgress.ResultType.Cleared))
Story.interact('clockmon')
assert(Story.debriefed('DigimonStory_FaultlineRidge') and unlocked.trickster_woods)

-- The third request accepts, clears, and archives only its own native record.
Story.interact('clockmon')
assert(SV.missions.Missions.DigimonStory_TricksterWoods ~= nil)
assert(Story.objective_met('DigimonStory_TricksterWoods'))
assert(Story.on_zone_exit('trickster_woods', 0, RogueEssence.Data.GameProgress.ResultType.Cleared))
Story.interact('clockmon')
assert(Story.debriefed('DigimonStory_TricksterWoods'))
assert(unlocked.overgrown_wilds and unlocked.moonlit_courtyard)
print('Passed Clockmon primary-request acceptance, failure, clear, debrief, and route-unlock scenarios')
