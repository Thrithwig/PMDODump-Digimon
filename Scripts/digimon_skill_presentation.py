"""PMDO-native visual and targeting profiles for Cyber Sleuth attacks."""

MELEE = {'Neutral':'pound','Fire':'fire_punch','Water':'ice_punch','Plant':'leaf_blade',
         'Electric':'thunder_punch','Thunder':'thunder_punch','Earth':'rock_smash',
         'Wind':'peck','Light':'karate_chop','Dark':'bite'}
SHOT = {'Neutral':'psybeam','Fire':'flamethrower','Water':'water_pulse','Plant':'energy_ball',
        'Electric':'charge_beam','Thunder':'charge_beam','Earth':'mud_slap',
        'Wind':'aeroblast','Light':'signal_beam','Dark':'shadow_ball'}
BURST = {'Neutral':'swift','Fire':'heat_wave','Water':'bubble','Plant':'petal_blizzard',
         'Electric':'discharge','Thunder':'discharge','Earth':'earthquake',
         'Wind':'gust','Light':'dazzling_gleam','Dark':'dark_pulse'}


def profile(entry):
    source = entry['variants'][0]['source']
    name = entry['name'].lower()
    element = source['Attribute']
    area = 'all foes' in source['Description'].lower()
    if source['Type'] == 'Support':
        return None
    if source['Type'] == 'Physical':
        if area:
            return BURST[element], 'burst', 2, 4
        if any(word in name for word in ('rush', 'charge', 'tackle', 'dash', 'assault', 'impulse')):
            return 'quick_attack', 'dash', 3, 4
        return MELEE[element], 'melee', 1, 4
    if area:
        return BURST[element], 'burst', 3, 4
    # Beam/cannon shots stop at the first creature; guided energy shots pass allies.
    direct = any(word in name for word in ('beam', 'cannon', 'laser', 'blast', 'breath', 'spit', 'shot'))
    return SHOT[element], 'projectile', 6 if direct else 4, 6 if direct else 4


def apply(obj, selected):
    _, shape, distance, targets = selected
    action = obj['HitboxAction']
    action['TargetAlignments'] = targets
    obj['Explosion']['TargetAlignments'] = targets
    obj['Explosion']['Range'] = 0
    # Keep the native emitter/action class, but bound the dungeon reach explicitly.
    if 'Range' in action:
        action['Range'] = distance
    if 'StopAtHit' in action:
        action['StopAtHit'] = True
    if 'StopAtWall' in action:
        action['StopAtWall'] = True
    if 'Rays' in action:
        action['Rays'] = 0
    if shape == 'melee' and 'WideAngle' in action:
        action['WideAngle'] = 0
    if shape == 'burst' and 'HitArea' in action:
        action['HitArea'] = 0
    if shape == 'melee': return 'Strikes the adjacent foe in front.'
    if shape == 'dash': return 'Dashes up to 3 tiles, stopping at the first foe or wall.'
    if shape == 'burst': return f'Hits foes within {distance} tiles; allies are safe.'
    return f'Fires up to {distance} tiles, stopping at walls and the first ' + ('friend or foe.' if targets == 6 else 'foe; passes allies safely.')
