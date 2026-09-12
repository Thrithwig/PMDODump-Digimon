local Ledger = require 'origin.digimon.scan_ledger'
local Catalog = require 'origin.digimon.catalog'
local Terminal = require 'origin.digimon.terminal'
local Serpent = require 'lib.serpent'
local count = 0
local function test(name, fn)
  local ok, reason = pcall(fn)
  assert(ok, name .. ': ' .. tostring(reason))
  count = count + 1
end
local function event(state, id, kind)
  return { entity_id = id, species = 'agumon', confirmed = true, source_kind = kind or 'hostile',
           floor_sequence = state.floor.sequence, source_name = 'Test dungeon', variant = 'normal' }
end
local function unlocked()
  local state = Ledger.new()
  Ledger.begin_floor(state)
  for i = 1, 4 do Ledger.award(state, Catalog, event(state, tostring(i))) end
  return state
end

test('four eligible defeats unlock once and duplicate events do not count', function()
  local state = Ledger.new()
  Ledger.begin_floor(state)
  for i = 1, 4 do
    local e = event(state, tostring(i))
    local result = Ledger.award(state, Catalog, e)
    assert(result.points == 25 * i)
    assert(result.unlocked == (i == 4))
    assert(Ledger.award(state, Catalog, e) == nil)
  end
  local row = Ledger.get(state, 'agumon')
  assert(row.unlock_count == 1 and row.first_source == 'Test dungeon')
  assert(row.variants_discovered.normal)
end)

test('excluded sources unconfirmed and unknown creatures award nothing', function()
  local state = Ledger.new()
  Ledger.begin_floor(state)
  for _, kind in ipairs({'summon', 'illusion', 'friendly', 'neutral', 'pvp_ghost', 'scripted_defeat'}) do
    assert(Ledger.award(state, Catalog, event(state, kind, kind)) == nil)
  end
  local e = event(state, 'alive'); e.confirmed = false
  assert(Ledger.award(state, Catalog, e) == nil)
  e.confirmed = true; e.species = 'pikachu'
  assert(Ledger.award(state, Catalog, e) == nil)
  assert(next(state.species) == nil)
end)

test('floor cap is per species while the total can exceed 100', function()
  local state = unlocked()
  assert(Ledger.award(state, Catalog, event(state, '5')).bits == 0)
  local e = event(state, '6'); e.species = 'gabumon'
  assert(Ledger.award(state, Catalog, e).points == 25)
  Ledger.begin_floor(state)
  local gain=Ledger.award(state, Catalog, event(state, '1'))
  assert(gain.bits == 0 and gain.points == 125)
  assert(Ledger.get(state, 'agumon').unlock_count == 1)
  e = event(state, 'old'); e.floor_sequence = 1
  assert(Ledger.award(state, Catalog, e) == nil)
end)

test('save roundtrip retains ledger floor caps and processed spawn identities', function()
  local state = unlocked()
  local restored = assert(load(Serpent.dump(state)))()
  assert(Ledger.valid(restored))
  assert(Ledger.get(restored, 'agumon').code_unlocked)
  assert(Ledger.award(restored, Catalog, event(restored, '1')) == nil)
  assert(Ledger.award(restored, Catalog, event(restored, 'new')).credited == 0)
end)

local function adapter()
  local reserves = {}
  return {
    ready = function(id) return #reserves == 0, 'Already in reserves' end,
    prepare = function(id, level) return { BaseForm = { Species = id }, Level = level } end,
    commit = function(char) table.insert(reserves, char) end,
    rollback = function(char) for i = #reserves, 1, -1 do if reserves[i] == char then table.remove(reserves, i) end end end,
    reserves = reserves
  }
end

test('restore requires an unlocked code and adds one reserve with full active team', function()
  local a = adapter()
  local locked = Ledger.new()
  assert(not Ledger.restore(locked, 'agumon', a))
  local state = unlocked()
  assert(Ledger.restore(state, 'agumon', a))
  assert(#a.reserves == 1 and a.reserves[1].BaseForm.Species == 'agumon')
  assert(a.reserves[1].Level == 5)
  assert(Ledger.get(state, 'agumon').restoration_count == 1)
  assert(not Ledger.restore(state, 'agumon', a))
  assert(#a.reserves == 1)
end)

test('failed preparation and commit do not consume code or retain partial reserve', function()
  local state = unlocked()
  local a = adapter()
  a.prepare = function() error('missing skill') end
  assert(not Ledger.restore(state, 'agumon', a))
  a = adapter()
  a.commit = function(char) table.insert(a.reserves, char); error('commit failure') end
  assert(not Ledger.restore(state, 'agumon', a))
  assert(#a.reserves == 0)
  assert(Ledger.get(state, 'agumon').restoration_count == 0)
  assert(Ledger.get(state, 'agumon').code_unlocked)
end)

local function ui(queue)
  local messages = {}
  UI = {
    BeginChoiceMenu = function() end, BeginMultiPageMenu = function() end,
    ChoiceMenuYesNo = function() end, WaitForChoice = function() end,
    ChoiceResult = function() assert(#queue > 0, 'UI queue exhausted'); return table.remove(queue, 1) end,
    WaitShowDialogue = function(_, message) table.insert(messages, message) end
  }
  return messages
end

test('existing adventuring team action remains available including old saves', function()
  SV = {}
  local calls = 0
  local messages = ui({1, 2, 5})
  Terminal.show(function() calls = calls + 1 end, adapter())
  assert(calls == 1 and #messages == 1 and SV.Digimon == nil)
end)

test('ledger browse and cancel have no side effects', function()
  SV = { Digimon = Ledger.new() }
  ui({2, 1, #Catalog.species+1, 5})
  Terminal.show(function() error('wrong action') end, adapter())
  assert(next(SV.Digimon.species) == nil)
end)

test('cancel restoration confirmation creates nothing', function()
  SV = { Digimon = unlocked() }
  local a = adapter()
  ui({3, 1, false, 2, 5})
  Terminal.show(function() end, a)
  assert(#a.reserves == 0 and Ledger.get(SV.Digimon, 'agumon').restoration_count == 0)
end)

test('confirmed restoration goes to reserves and is visible in ledger', function()
  SV = { Digimon = unlocked() }
  local a = adapter()
  local messages = ui({3, 1, true, 5})
  Terminal.show(function() end, a)
  assert(#a.reserves == 1 and messages[1]:find('restored to your reserves'))
  assert(Ledger.get(SV.Digimon, 'agumon').restoration_count == 1)
end)

local function trainee(level)
  local char = { BaseForm = { Species = 'agumon' }, Level = level, RewardIdentity = 'trainee', Nickname = 'Agumon',
                 MaxHPBonus = 0, AtkBonus = 0, DefBonus = 0, MAtkBonus = 0, MDefBonus = 0, SpeedBonus = 0 }
  function char:GetDisplayName() return self.Nickname end
  return char
end

test('training menu assigns and clears a regimen and offers reserve level-up skills', function()
  SV = { Digimon = Ledger.new() }
  local char = trainee(12)
  local checks = {}
  GAME = { GetPlayerPartyTable = function() return {} end, GetPlayerAssemblyTable = function() return { char } end,
           CheckLevelSkills = function(_, target, from) table.insert(checks, { target, from }) end }
  local messages = ui({ 4, 1, 2, 2, 5 })
  Terminal.show(function() error('wrong action') end, adapter())
  local row = SV.Digimon.characters.trainee
  assert(row.regimen == 'AtkBonus' and messages[1]:find('will train Attack') and #checks == 0)
  row.skill_check_level = 7
  messages = ui({ 4, 1, 10, 2, 5 })
  Terminal.show(function() end, adapter())
  assert(row.regimen == nil and messages[1]:find('will rest'))
  assert(#checks == 1 and checks[1][1] == char and checks[1][2] == 7 and row.skill_check_level == nil)
  ui({ 4, 2, 5 })
  Terminal.show(function() end, adapter())
  assert(row.regimen == nil)
end)

test('training is refused on old saves without touching the team', function()
  SV = {}
  GAME = { GetPlayerPartyTable = function() error('must not read team') end }
  local messages = ui({ 4, 5 })
  Terminal.show(function() end, adapter())
  assert(#messages == 1 and messages[1]:find('fresh save'))
end)

test('missing engine records refuse restoration without fallback', function()
  GAME = { GetPlayerPartyTable = function() return {} end, GetPlayerAssemblyTable = function() return {} end }
  RogueEssence = { Data = { DataManager = { DataType = { Monster = 'monster', Skill = 'skill' } } } }
  local calls = 0
  _DATA = { DataIndices = { monster = { Get = function() error('unknown species') end } },
            GetMonster = function() calls = calls + 1; return {} end }
  local ready, reason = Terminal.engine_adapter().ready('agumon')
  assert(not ready and reason:find('not available') and calls == 0)
end)

-- Exercise the adapter with C#-shaped collections, not an alternate restoration implementation.
test('engine adapter uses installed species explicit identity and reserve APIs', function()
  local reserves = {}
  GAME = {
    GetPlayerPartyTable = function() return {{BaseForm={Species='gabumon'}}, {BaseForm={Species='biyomon'}},
                                           {BaseForm={Species='palmon'}}, {BaseForm={Species='patamon'}}} end,
    GetPlayerAssemblyTable = function() return reserves end,
    GetPlayerAssemblyCount = function() return #reserves end,
    GetPlayerAssemblyMember = function(_, i) return reserves[i+1] end,
    AddPlayerAssembly = function(_, char) table.insert(reserves, char) end,
    RemovePlayerAssembly = function(_, i) table.remove(reserves, i+1) end
  }
  Gender = { Genderless = 0 }
  _ZONE = { CurrentZoneID = 'hub', CurrentMapID = -1 }
  RogueEssence.Dungeon = {
    MonsterID = function(id, form, skin, gender) return { Species=id, Form=form, Skin=skin, Gender=gender } end,
    ZoneLoc = function() return {} end, BattleScriptEvent = function(id) return id end
  }
  local form = { Released=true, Intrinsic1='none', LevelSkills={Count=1, [0]={Skill='pepper_breath',Level=1}} }
  local monster = { Released=true, Forms={ Count=1, [0]=form } }
  _DATA = {
    DefaultSkin='normal', DataIndices={monster={Get=function() return {Released=true} end}, skill={Get=function() return {} end}},
    GetMonster=function(_, id) assert(id=='agumon'); return monster end,
    Save={Rand={}, ActiveTeam={CreatePlayer=function(_, rand, id, level, intrinsic, personality)
      assert(id.Species=='agumon' and level==5 and intrinsic=='none' and personality==0)
      return {BaseForm=id,LuaDataTable={},ActionEvents={Add=function() end}}
    end}}
  }
  local state = unlocked()
  local a = Terminal.engine_adapter()
  assert(Ledger.restore(state, 'agumon', a))
  assert(#reserves == 1 and reserves[1].MetAt == 'Restoration terminal')
  assert(a.ready('agumon'))
end)

test('restoration spends all points and applies each complete extra 100', function()
  assert(Ledger.restoration_level(99)==nil)
  for _,sample in ipairs({{100,5},{199,5},{200,10},{300,15},{2000,99},{10000,99}}) do
    local state=unlocked();state.species.agumon.scan_points=sample[1]
    local a=adapter()
    assert(Ledger.restore(state,'agumon',a))
    assert(a.reserves[1].Level==sample[2])
    assert(state.species.agumon.scan_points==0 and not state.species.agumon.code_unlocked)
    assert(not Ledger.restore(state,'agumon',a))
    Ledger.begin_floor(state)
    for i=1,4 do Ledger.award(state,Catalog,event(state,tostring(i))) end
    a.ready=function() return true end
    assert(Ledger.restore(state,'agumon',a) and #a.reserves==2)
  end
end)

test('failed restoration retains all banked scan points',function()
  local state=unlocked();state.species.agumon.scan_points=325
  local a=adapter();a.commit=function(char) table.insert(a.reserves,char);error('fail') end
  assert(not Ledger.restore(state,'agumon',a))
  assert(state.species.agumon.scan_points==325 and state.species.agumon.code_unlocked and #a.reserves==0)
end)

print('Passed ' .. count .. ' Lua terminal/ledger scenarios')
