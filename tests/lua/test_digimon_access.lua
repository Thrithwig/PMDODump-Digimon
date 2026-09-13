local Access=require 'origin.digimon.dungeon_access'
local Ledger=require 'origin.digimon.scan_ledger'
local unlocked={tropical_path=true,faultline_ridge=false,trickster_woods=false}
local cleared={}
SV={Digimon=Ledger.new(),team_kidnapped={Status=2},forest_camp={ExpositionComplete=false}}
GAME={DungeonUnlocked=function(_,id) return unlocked[id] end,
  UnlockDungeon=function(_,id) unlocked[id]=true end}
local ZoneLoc={Invalid={IsValid=function() return false end}}
setmetatable(ZoneLoc,{__call=function(_,id,segment,floor,entry)
  return {ID=id,StructID={Segment=segment,ID=floor},EntryPoint=entry,IsValid=function() return true end}
end})
RogueEssence={Dungeon={ZoneLoc=ZoneLoc,MonsterID=function(id) return {Species=id} end},Data={DataManager={DataType={Zone='Zone'}},
  GameProgress={UnlockState={Completed=2},DungeonStakes={Risk=1}}}}
_DATA={Save={GetDungeonUnlock=function(_,id) return cleared[id] and 2 or 1 end},DataIndices={Zone={Get=function(_,id)
  return {Released=true,Name={ToLocal=function() return id end},GetColoredName=function() return id end} end}},PreLoadZone=function() end}
local base={'guildmaster_trail','tropical_path','faultline_ridge'}
assert(#Access.destinations(base)==2)
assert(#Access.destinations({})==0) -- south exits and ferries do not gain global destinations
assert(#Access.destinations({'trickster_woods'})==0)
assert(SV.team_kidnapped.Status==2 and not SV.forest_camp.ExpositionComplete)
cleared.tropical_path=true
SV.Digimon.StoryMissions.records.DigimonStory_TropicalPath.debriefed=true
SV.forest_camp.ExpositionComplete=true
assert(#Access.destinations(base)==3)
assert(Access.grounds({{Zone='guildmaster_island',ID=3,Entry=0,Flag=false}})[1].Flag)
assert(#Access.destinations({'trickster_woods'})==0)
cleared.faultline_ridge=true
SV.Digimon.StoryMissions.records.DigimonStory_FaultlineRidge.debriefed=true
assert(#Access.destinations({'trickster_woods'})==1)
assert(Access.entry_floor('training_maze')==4)
SOUND={PlaySE=function() end,PlayBGM=function() end}
GAME.FadeOut=function() end
for index,id in ipairs(base) do
  local choice,entered=0,false
  UI={ResetSpeaker=function() end,WaitForChoice=function() end,
    DestinationMenu=function(_,rows) assert(#rows==3);assert(rows[index].Dest.ID==id) end,
    DungeonChoice=function(_,name,dest) assert(dest.ID==id) end,
    ChoiceResult=function() choice=choice+1;if choice==1 then return index else return true end end}
  GAME.EnterDungeon=function(_,zone,segment,floor,entry)
    assert(zone==id and segment==0 and floor==0 and entry==0);entered=true
  end
  COMMON.ShowDestinationMenu(base, {})
  assert(entered,id..' not dispatched')
end
-- Exercise the actual service with fixed NPCs, scripted spawners and party exclusion.
package.loaded['origin.services.baseservice']=true
Class=function() local c={};function c:new() return setmetatable({},{__index=self}) end;return c end
local service
SCRIPT={AddService=function(_,name,instance) service=instance end}
Gender={Genderless=-1}
package.loaded['origin.services.digimon_runtime']=nil
require 'origin.services.digimon_runtime'
local function actor(id)
 return {BaseForm={Species=id},Promote=function(self,form) self.BaseForm=form end}
end
for _,camp in ipairs({'base_camp','base_camp_2','forest_camp','cliff_camp','canyon_camp','rest_stop','final_stop'}) do
 local npc=actor('pikachu');local sleeper=actor('snorlax');local spawner=actor('eevee');local ally=actor('agumon')
 local map={Entities={Count=1,[0]={MapChars={Count=2,[0]={Data=npc,EntName='NPC'},[1]={Data=sleeper,EntName='Snorlax'}},
   Spawners={Count=2,[0]={NPCChar=spawner,EntName='NPC_Guide'},[1]={NPCChar=ally,EntName='ASSEMBLY_1'}}}}}
 service:Ground(camp,map)
 local runtime=require 'origin.digimon.runtime_catalog'
 assert(runtime.species[npc.BaseForm.Species] and runtime.species[spawner.BaseForm.Species])
 assert(sleeper.BaseForm.Species=='monzaemon' and ally.BaseForm.Species=='agumon')
end
SV.Digimon=nil
local original={'tropical_path'}
assert(Access.destinations(original)==original)
assert(Access.entry_floor('training_maze')==0)
print('Passed camp routing, legacy-save gates, menu dispatch and seven-camp NPC conversion scenarios')
