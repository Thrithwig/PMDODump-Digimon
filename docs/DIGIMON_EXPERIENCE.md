# EXP requirements and rewards

All 341 Digimon use identical level-up requirements (the tested Rookie curve).
Existing stage growth-group IDs are retained for save compatibility and identify
recipient stage when computing battle rewards; their level-up tables are identical.

Enemy-defeat EXP uses floor(BaseEXP * (enemy level - 1) / 10) + BaseEXP,
then the recipient-stage multiplier: Baby/In-Training 2, Rookie 1.5,
Champion 1, Ultimate 0.75, Mega 0.5. The existing overlevel penalty also applies;
the final reward is rounded down. Both active-party and eligible assembly members
use their own stage. Item EXP is unchanged.

For a 100 EXP reward without an overlevel penalty, the six stages receive
200, 200, 150, 100, 75 and 50 EXP respectively. These cases, fractional rounding,
and anti-farming behavior are checked by the native runtime tests.
