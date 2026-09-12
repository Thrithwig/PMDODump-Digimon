local Sync=require 'origin.digimon.passive_abilities'
local expected={agumon='digi_agumon_test',gabumon='digi_gabumon_test'}
local reads=0
_DATA={GetMonster=function(_,species)
  reads=reads+1
  assert(expected[species], 'Non-Digimon should not read monster data')
  return {Forms={[0]={Intrinsic1=expected[species]}}}
end}
local function actor(species,ability)
  return {BaseForm={Species=species,Form=0},BaseIntrinsics={[0]=ability},calls=0,
    LearnIntrinsic=function(self,id,slot)
      assert(slot==0,'Must use primary intrinsic slot')
      self.calls=self.calls+1
      self.BaseIntrinsics[slot]=id
    end}
end
-- Old saves migrate through LearnIntrinsic, not direct field assignment.
local old=actor('agumon','none')
assert(Sync.sync(old))
assert(old.BaseIntrinsics[0]==expected.agumon and old.calls==1)
assert(not Sync.sync(old))
assert(old.calls==1)
local pokemon=actor('pikachu','static')
local reads_before=reads
assert(not Sync.sync(pokemon))
assert(pokemon.BaseIntrinsics[0]=='static' and pokemon.calls==0 and reads==reads_before)
-- Party and storage have independent migration paths, including repeat calls.
local party=actor('agumon','none')
local assembly=actor('gabumon','none')
GAME={GetPlayerPartyTable=function() return {party,pokemon} end,
      GetPlayerAssemblyTable=function() return {assembly} end}
Sync.team()
assert(party.BaseIntrinsics[0]==expected.agumon and party.calls==1)
assert(assembly.BaseIntrinsics[0]==expected.gabumon and assembly.calls==1)
Sync.team()
assert(party.calls==1 and assembly.calls==1 and pokemon.calls==0)
assert(not Sync.sync(nil))
assert(not Sync.sync({}))
assert(not Sync.sync({BaseForm={Species='agumon'}}))
GAME={}
Sync.team()
-- A stale/unconverted template must not erase a working ability.
expected.agumon='none'
assert(not Sync.sync(party))
assert(party.BaseIntrinsics[0]=='digi_agumon_test' and party.calls==1)
print('Passed passive migration, idempotence, party/assembly and non-Digimon isolation scenarios')
