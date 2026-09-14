-- Exercise the actual rescue dialogue handler, not just mission flag helpers.
local Story = require 'origin.digimon.story_missions'
COMMON.MISSION_COMPLETE = 1
SV.Digimon = {}
SV.missions = { Missions = {}, FinishedMissions = {} }
Story.accept('DigimonStory_TropicalPath')
local accepted = false
local removed = {}
local asked = {}
LTBL = function(char) return char.LuaDataTable end
_DATA = { GetMonster = function(_, species)
  return { Name = { ToLocal = function() return species end } }
end }
RogueEssence.StringKey = function(key) return { ToLocal = function() return key end } end
RogueEssence.Dungeon.CharAnimPose = function() return {} end
STRINGS = { Format = function(_, key, name)
  if key == 'DLG_MISSION_RESCUE_ASK' then asked[#asked + 1] = name end
  return key
end }
UI = { ResetSpeaker = function() end, SetSpeaker = function() end,
  ChoiceMenuYesNo = function() end, WaitForChoice = function() end,
  ChoiceResult = function() return accepted end, WaitShowDialogue = function() end }
DUNGEON = { CharTurnToChar = function() end, CharSetAction = function() end, CharEndAnim = function() end }
_DUNGEON = { ProcessBattleFX = function() end,
  RemoveChar = function(_, char) removed[#removed + 1] = char.BaseForm.Species end }
TASK = { WaitTask = function() end }
local function rescue(species)
  local context = { User = {}, Target = { BaseForm = { Species = species },
    LuaDataTable = { Mission = 'DigimonStory_TropicalPath' } },
    TurnCancel = {}, CancelState = {} }
  BATTLE_SCRIPT.SidequestRescueReached(nil, nil, context, {})
  return context
end
assert(rescue('falcomon').CancelState.Cancel)
assert(#removed == 0 and #Story.rescue_targets('DigimonStory_TropicalPath') == 3)
accepted = true
for index, species in ipairs({'falcomon', 'botamon', 'punimon'}) do
  assert(rescue(species).TurnCancel.Cancel)
  assert(asked[#asked] == species)
  assert(removed[index] == species)
  local mission = SV.missions.Missions.DigimonStory_TropicalPath
  assert(mission.Complete == (index == 3 and COMMON.MISSION_COMPLETE or COMMON.MISSION_INCOMPLETE))
end
assert(SV.Digimon.StoryMissions.records.DigimonStory_TropicalPath.objective_met)
print('Passed actual three-target rescue interactions, cancellation, names, and completion gating')
