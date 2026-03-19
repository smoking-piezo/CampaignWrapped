#! python3

from dataclasses import dataclass
import datetime

@dataclass
class roll():
    date_time: datetime.datetime
    roller: str
    type: object
    # roll_lines: list

class attack_roll:
    roll_type = "Attack"

    def __init__(self, to_hit_d20, dmg_d20):
        self.to_hit_d20 = to_hit_d20
        self.dmg_d20 = dmg_d20

class initiative():
    roll_d20: float
    roll_mod: float

def main():
    attack = attack_roll(20, 15)
    first_roll = roll((2020, 12, 10), "piezo", attack)

    init_roll = (20.05, 40.05)
    second_roll = roll((2020, 12, 12), "monk", init_roll)

    print(first_roll.date_time, first_roll.roll_type, second_roll.roller)

main()
