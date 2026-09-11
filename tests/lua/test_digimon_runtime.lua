local Ledger=require 'origin.digimon.scan_ledger'
local Runtime=require 'origin.digimon.runtime_catalog'
local Progress=require 'origin.digimon.progression'
local Serpent=require 'lib.serpent'
local count=0
local function test(name,fn)
  local ok,err=pcall(fn);assert(ok,name..': '..tostring(err));count=count+1
end
local function setup(species,level)
  SV={Digimon=Ledger.new()}
  _ZONE={CurrentGround={AssetName='luminous_spring'}}
  _DATA={DataIndices={monster={Get=function() return {} end}},
    GetMonster=function() return {Forms={[0]={Released=true,GetStat=function(self,level,stat,bonus) return 10+level+bonus end}},EXPTable='test'} end,
    GetGrowth=function() return {GetExpToNext=function() return 100 end} end,
    Save={RegisterMonster=function() end}}
  RogueEssence={Data={Stat={HP='HP',Attack='Attack',Defense='Defense',MAtk='MAtk',MDef='MDef',Speed='Speed'},DataManager={DataType={Monster='monster'}}},Dungeon={
    MonsterID=function(id,form,skin,gender) return {Species=id,Form=form,Skin=skin,Gender=gender} end}}
  Gender={Genderless=0};COMMON={RespawnAllies=function() end}
  local char={BaseForm={Species=species,Form=0,Skin='normal',Gender=0},Level=level,EXP=55,
    HP=500,MaxHP=1000,BaseAtk=999,BaseDef=999,BaseMAtk=999,BaseMDef=999,BaseSpeed=999,
    MaxHPBonus=0,AtkBonus=0,DefBonus=0,MAtkBonus=0,MDefBonus=0,SpeedBonus=0,
    RewardIdentity='unique-character',Nickname='Partner',EquippedItem={ID='held'},BaseSkills={'known'}}
  function char:Promote(form) self.BaseForm=form end
  return char
end
local function edge(from,to)
  for _,x in ipairs(Runtime.transitions) do if x.from==from and x.to==to then return x end end
  error('No edge '..from..' -> '..to)
end

test('every selected transition applies while preserving character identity',function()
  for _,e in ipairs(Runtime.transitions) do
    local c=setup(e.from,99);local row=Progress.progress(c);row.bond=100;row.abi=200;row.sp_bonus=256
    local party={c};local bag={}
    for _,req in ipairs(e.requirements) do
      if req.kind=="party" and req.species~=c.BaseForm.Species then table.insert(party,{BaseForm={Species=req.species},Level=req.minimum}) end
      if req.kind=="item" then table.insert(bag,{ID=req.item}) end
    end
    GAME={GetPlayerPartyTable=function() return party end,GetPlayerBagCount=function() return #bag end,GetPlayerBagItem=function(_,i) return bag[i+1] end}
    local held,skills=c.EquippedItem,c.BaseSkills
    assert(Progress.change(c,e))
    assert(c.BaseForm.Species==e.to and c.RewardIdentity=='unique-character' and c.Nickname=='Partner')
    assert(c.EquippedItem==held and c.BaseSkills==skills and c.HP==500)
    assert(c.Level==1 and c.EXP==0)
  end
end)

test('fusion requires both actual active partners at the required level',function()
  local c=setup('wargreymon',99); local donor=setup('metalgarurumon',59)
  local row=Progress.progress(c);row.bond=100;row.abi=200;row.sp_bonus=256
  local party={c,donor};GAME={GetPlayerPartyTable=function() return party end}
  local e=edge('wargreymon','omnimon')
  assert(not Progress.preview(c,e))
  donor.Level=60;assert(Progress.preview(c,e))
  party={c};assert(not Progress.preview(c,e))
  party={donor,{BaseForm={Species='wargreymon'},Level=99}};assert(not Progress.preview(c,e))
  party={c,donor};assert(Progress.change(c,e))
  assert(donor.BaseForm.Species=='metalgarurumon' and donor.Level==60)
end)

test('item gate checks inventory again at commit and never grants a free unlock',function()
  local c=setup('veemon',99);local row=Progress.progress(c);row.bond=100;row.abi=200;row.sp_bonus=256
  local bag={};GAME={GetPlayerPartyTable=function() return {c} end,
    GetPlayerBagCount=function() return #bag end,GetPlayerBagItem=function(_,i) return bag[i+1] end}
  local e=edge('veemon','flamedramon')
  assert(not Progress.change(c,e));bag={{ID='evo_sun_stone'}};assert(Progress.preview(c,e))
  bag={};assert(not Progress.change(c,e));c.EquippedItem={ID='evo_sun_stone'}
  assert(Progress.change(c,e));assert(c.EquippedItem.ID=='evo_sun_stone')
end)

test('requirements and geography reject changes',function()
  local c=setup('agumon',5);local e=edge('agumon','greymon')
  assert(not Progress.change(c,e));assert(c.BaseForm.Species=='agumon' and c.EXP==55)
  c.Level=99;_ZONE.CurrentGround.AssetName='forest_camp'
  assert(not Progress.change(c,e));assert(c.BaseForm.Species=='agumon')
end)

test('devolution retains earned training and does not reward immediate toggles',function()
  local c=setup('agumon',65)
  assert(Progress.change(c,edge('agumon','koromon')))
  local p=Progress.progress(c)
  assert(c.Level==1 and c.EXP==0 and c.AtkBonus==12 and p.abi==72)
  local abi=p.abi
  assert(not Progress.change(c,edge('koromon','agumon')))
  assert(Progress.change(c,edge('koromon','botamon')))
  assert(c.AtkBonus==12 and p.abi==abi)
  c.Level=21
  assert(Progress.change(c,edge('botamon','koromon')))
  assert(c.Level==1 and c.EXP==0)
  c.Level=21
  assert(Progress.change(c,edge('koromon','botamon')))
  assert(c.Level==1 and c.AtkBonus==20 and p.abi>abi)
  local ok,saved=Serpent.load(Serpent.block(SV.Digimon));assert(ok)
  assert(saved.characters[c.RewardIdentity].abi==p.abi)
end)

test('retains twenty percent of actual stat growth and new training in both directions',function()
  local c=setup('agumon',65)
  local row=Progress.progress(c);row.bond=100;row.abi=200
  c.AtkBonus=25
  assert(Progress.change(c,edge('agumon','greymon')))
  assert(c.Level==1 and c.EXP==0 and c.AtkBonus==17 and c.MaxHPBonus==12)
  assert(c.LuaDataTable.DigimonRetainedAtkBonus==17)
  assert(Progress.change(c,edge('greymon','agumon')))
  assert(c.AtkBonus==17 and c.MaxHPBonus==12)
  c.Level=21;c.AtkBonus=c.AtkBonus+20
  assert(Progress.change(c,edge('agumon','koromon')))
  assert(c.AtkBonus==25 and c.MaxHPBonus==16)
  local ok,saved=Serpent.load(Serpent.block(SV.Digimon));assert(ok)
  assert(saved.characters[c.RewardIdentity].retained.AtkBonus==25)
end)

test('failed native promotion rolls form level experience and bonuses back',function()
  local c=setup('agumon',65);local calls=0
  function c:Promote(form)
    calls=calls+1;self.BaseForm=form
    if calls==1 then error('injected failure') end
  end
  local p=Progress.progress(c);local abi=p.abi
  assert(not Progress.change(c,edge('agumon','koromon')))
  assert(c.BaseForm.Species=='agumon' and c.Level==65 and c.EXP==55 and c.AtkBonus==0 and c.HP==500)
  assert(p.abi==abi and p.cycle_start==5 and p.retained==nil and p.retained_sp==nil)
end)

test('restored levels do not grant free training and evolution resets level and EXP',function()
  local c=setup('agumon',65);c.LuaDataTable={DigimonRestoredLevel=65}
  local row=Progress.progress(c);assert(row.abi==0 and row.cycle_start==65)
  row.abi=100;row.bond=100
  local calls=0
  _DATA.GetGrowth=function()
    calls=calls+1;local need=calls==1 and 100 or 200
    return {GetExpToNext=function() return need end}
  end
  assert(Progress.change(c,edge('agumon','greymon')) and c.EXP==0 and c.Level==1)
  assert(Progress.change(c,edge('greymon','agumon')))
  assert(c.Level==1 and c.AtkBonus==0)
end)

test('personality food has no elemental dependence and caps bonuses',function()
  local c=setup('agumon',5);c.Fullness=0;c.MaxFullness=100
  local effects=require 'origin.digimon.item_effects';local row=Progress.progress(c)
  row.personality='Durable';effects.food(c,'AtkBonus')
  assert(c.AtkBonus==1 and c.MaxHPBonus==50 and c.Fullness==5)
  row.personality='Builder';effects.food(c,'DefBonus')
  assert(c.AtkBonus==2 and c.DefBonus==2 and row.development_time_multiplier==0.95)
  row.personality='Searcher';effects.food(c,'bond')
  assert(row.investigation_time_multiplier==0.95 and row.bond==15)
  c.MaxHPBonus=256;row.personality='Durable';effects.food(c,'MaxHPBonus');assert(c.MaxHPBonus==256)
end)

test('Brave Points award exact EXP through the real level-up queue contract',function()
  local c=setup('agumon',5);local queued=0
  _ZONE.CurrentMap={GetCharIndex=function(_,target) assert(target==c);return 12 end}
  _DUNGEON={LevelGains={Add=function(_,index) assert(index==12);queued=queued+1 end}}
  local effects=require 'origin.digimon.item_effects'
  for _,amount in ipairs({2500,5000,10000,20000,40000}) do
    c.EXP=0;assert(effects.experience(c,amount));assert(c.EXP==amount)
  end
  assert(queued==5);c.Level=99;assert(not effects.experience(c,40000));assert(queued==5)
end)

-- Exercise the real service adapter against C#-shaped map/team collections.
package.loaded['origin.services.baseservice']=true
Class=function() return {new=function(self) return setmetatable({},{__index=self}) end} end
SCRIPT={AddService=function(_,name,svc) SCRIPT.service=svc end}
require 'origin.services.digimon_runtime'
local service=SCRIPT.service

test('floor reload preserves ledger and service excludes friendly or untagged defeats',function()
  local c=setup('agumon',5)
  RogueEssence.Dungeon.Faction={Foe=2}
  _ZONE.CurrentZoneID='tropical_path'
  _ZONE.CurrentMap={GetCharFaction=function(_,char) return char.faction end}
  _DATA.Save.ActiveTeam={Money=0}
  GAME={GetPlayerPartyTable=function() return {c} end}
  _DUNGEON={LogMsg=function() end}
  service:Floor('',{RewardFloorIdentity='floor-one'})
  local seq=SV.Digimon.floor_sequence
  service:Floor('',{RewardFloorIdentity='floor-one'});assert(SV.Digimon.floor_sequence==seq)
  local foe={Dead=true,LuaDataTable={DigimonNatural=true},faction=2,BaseForm={Species='koromon',Form=0},RewardIdentity='spawn-1'}
  service:Defeat(foe);service:Defeat(foe)
  assert(Ledger.get(SV.Digimon,'koromon').scan_points==25 and Progress.progress(c).bond==11)
  foe.RewardIdentity='friendly';foe.faction=1;service:Defeat(foe)
  foe.RewardIdentity='summon';foe.faction=2;foe.LuaDataTable={};service:Defeat(foe)
  assert(Ledger.get(SV.Digimon,'koromon').scan_points==25)
  service:Floor('',{RewardFloorIdentity='floor-two'});assert(SV.Digimon.floor_sequence==seq+1)
end)

package.loaded['origin.common']=true
SINGLE_CHAR_SCRIPT={}
luanet={import_type=function() return {} end}
require 'origin.event_single'
test('guardian locks both exits only until defeated',function()
  local boss={Dead=false,LuaDataTable={DigimonBoss=true}}
  _ZONE={CurrentZoneID='tropical_path',CurrentMap={MapTeams={Count=1,[0]={Players={Count=1,[0]=boss}}}}}
  _DUNGEON={LogMsg=function() end}
  local context={CancelState={Cancel=false}}
  SINGLE_CHAR_SCRIPT.DigimonTropicalExit(nil,nil,context,{})
  assert(context.CancelState.Cancel)
  boss.Dead=true;context.CancelState.Cancel=false
  SINGLE_CHAR_SCRIPT.DigimonTropicalExit(nil,nil,context,{})
  assert(not context.CancelState.Cancel)
  boss.Dead=false;_ZONE.CurrentZoneID='other_zone'
  SINGLE_CHAR_SCRIPT.DigimonTropicalExit(nil,nil,context,{})
  assert(not context.CancelState.Cancel)
end)

print('Passed '..count..' Lua progression/service scenarios (including all 1812 transitions)')
