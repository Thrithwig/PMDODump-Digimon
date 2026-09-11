"""Explicit Phase 1 EXP tuning and Apricorn-only loot cleanup."""
from fractions import Fraction
import math

# Keep existing growth-group IDs compatible with saves; all use the tested Rookie pace.
STAGE_MULTIPLIERS = {stage: 1.5 for stage in ('Baby', 'In-Training', 'Rookie', 'Champion', 'Ultimate', 'Mega')}
BASE_EXP_PER_MEMORY = 24


def growth_table(base, stage):
    multiplier=Fraction(str(STAGE_MULTIPLIERS[stage]))
    result=[0]
    for previous,current in zip(base,base[1:]):
        result.append(result[-1]+math.ceil((current-previous)*multiplier))
    return result


def award(base_exp, defeated_level, recipient_level):
    reward=base_exp*(defeated_level-1)//10+base_exp
    gap=max(0,recipient_level-defeated_level-5)
    return 0 if gap>=10 else reward//(2**gap)


def remove_apricorns(value):
    """Remove item entries and their weighting wrappers, never entire rooms/zones."""
    if isinstance(value,list):
        return [clean for child in value if (clean:=remove_apricorns(child)) is not None]
    if not isinstance(value,dict): return value
    # A priority-list entry cannot retain a null generation operation.
    if 'Key' in value and 'Value' in value and value['Value'] is None:
        return None
    if any(isinstance(value.get(k),str) and value[k].startswith('apricorn_')
           for k in ('ID','Value','Item','HiddenValue')):
        return None
    clean={}
    for key,child in value.items():
        converted=remove_apricorns(child)
        if child is not None and converted is None and key in ('Spawn','ToSpawn','Item1'):
            return None
        clean[key]=converted
    if 'Key' in clean and 'Value' in clean and clean['Value'] is None:
        return None
    if isinstance(clean.get('Spawns'),dict):
        clean['Spawns']={k:v for k,v in clean['Spawns'].items()
                         if not (isinstance(v,dict) and v.get('Spawns')==[])}
    return clean
