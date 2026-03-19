#! python3

from dataclasses import dataclass
import datetime

@dataclass
class roll():
    date_time: datetime.datetime
    roller: str
    roll_type: object
    roll_lines: list

class attack_roll:
    roll_type = "Attack"

    def __init__(self, to_hit_d20, dmg_d20):
        self.to_hit_d20 = int(to_hit_d20)
        self.dmg_d20 = int(dmg_d20)

class init_roll():
    roll_type = "Initiative" 
    
    def __init__(self, roll_d20, roll_mod):
        roll_d20 = float(roll_d20)
        self.roll_d20 = roll_d20

        roll_mod = float(roll_mod)
        self.roll_mod = roll_mod


def main():
    '''
    attack = attack_roll(20, 15)
    first_roll = roll((2020, 12, 10), "piezo", attack)

    initiative = init_roll(20.05, 40.05)
    second_roll = roll((2020, 12, 12), "monk", initiative)

    print(first_roll.date_time, first_roll.roll_type, second_roll.roller, second_roll.roll_type)
    '''

    roll_box = []

    a_roll = ['----', '(2020, 12, 10)', 'roller', 'attack', 'attack 20 damage 15', 'pew pew']
    b_roll = ['----', '(2020, 12, 12)', 'roller', 'stealth skill check', '50', 'd20 + mods = 15 + 35', 'very sneak']

    
    # do we have to know the type of roll when we create the roll this way?
    roll_box.append(roll(a_roll[1],a_roll[2], attack_roll, a_roll))

    a_roll_type = roll_box[0].roll_type

    print(a_roll_type)

    attack = attack_roll(20,15)

    roll_box[0].roll_type = attack

    a_roll_type = roll_box[0].roll_type

    a_roll_type = a_roll_type.dmg_d20

    print(a_roll_type)




main()
