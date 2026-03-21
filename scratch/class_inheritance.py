#! python 3 

from dataclasses import dataclass
import datetime

@dataclass
class log_entry():
    acceptable_types = ["Unknown", "Initiative", "Attack"]
    def __init__(self, date_time, roller, log_lines, entry_type, roll_bin=[]):
        self.date_time = date_time
        self.roller = roller
        self.log_lines = log_lines 
        self.roll_bin = roll_bin
        self.roll_count = len(roll_bin)
        if entry_type in self.acceptable_types:
            self.entry_type = entry_type
        else:
            self.entry_type = "Unknown"
       

class dice_roll(log_entry):
    def __init__(self, date_time, roller, log_lines, die_roll_quant, roll_type="Unknown"):
        super().__init__(date_time, roller, log_lines)
        self.die_roll_quant = die_roll_quant
        if roll_type:
            self.roll_type = roll_type

class d20_roll(dice_roll):
    def __init__(self, date_time, roller, log_lines, roll_type, die_rolls_list):
        super().__init__(date_time, roller, log_lines, roll_type)
        self.die_rolls_list = die_rolls_list
        self.die_roll_quant = len(die_rolls_list)

class die_roll():
    def __init__(self, dx_type, dx_result, result_w_mods=0):
        self.dx_type = dx_type
        self.dx_result = dx_result
        if result_w_mods:
            self.result_w_mods = result_w_mods
        else: 
            self.result_w_mods = dx_result

class targeted_roll(die_roll):
    def __init__(self, dx_type, dx_result, result_w_mods, effect_roll):
        super().__init__(dx_type, dx_result, result_w_mods)
        self.effect_roll = effect_roll

def main():
    log = [["------","(2020, 10, 10)","roller name","stealth skill check", "30", "d20 + mods = 15 + 15", "very sneak"],["-------","(2010,12,15)","another roller","attack", "attack 20 damage 15","pew pew"]]
    entries = []

    for i in range(0,2):
        entry_date = log[i][1]
        entry_roller = log[i][2]
        entry_log = log[i]
        entries.append(log_entry(entry_date,entry_roller, "Unknown", entry_log))

    #entries[1]=dice_roll(entries[0].date_time, entries[0].roller,entries[0].log_lines, 1, "Attack")
    #entries[0]=d20_roll(entries[0].date_time, entries[0].roller, entries[0].log_lines, 1, "Skill", 15, 15)

    #new_entry = d20_roll((2025,1,1),"doggo",["list of lines"],"Save Throw", 20, 30)
    new_entry = ['------', '(2026,12,5)','attacker','attack','attack 21 damage 18', 'attack 2 15 damage 16', 'attack 3 16 crit 28 damage 16 32']
    #iter_attack = d20_roll((2026,12,5),"attacker",['------', 'datetime','attacker','attack','attack 16 damage 5', 'attack 2 10 damage 5', 'attack 3 20 crit 20 damage 20 50'],"Attack", 3, )
    iter_atk_dice = []
    atk_to_hit = [21, 15, 16]
    atk_dmg = [18, 16, 16]
    crit_tohit = [28]
    crit_dmg = [32]

    atk_1 = die_roll("d20",atk_to_hit[0])
    atk_2 = targeted_roll("d20",atk_to_hit[1], 0,atk_dmg[1])
    atk_3 = targeted_roll("d20", atk_to_hit[2], 0, atk_dmg[2])

    iter_atk_dice.append(atk_1)
    iter_atk_dice.append(atk_2)
    iter_atk_dice.append(atk_3)

    #iter_atk = d20_roll((2026,12,5), "attacker", new_entry, "Attack", iter_atk_dice)

    entry_test = log_entry(entries[0].date_time, "Actor", new_entry, "Attack", iter_atk_dice)

    print(entry_test.date_time, entry_test.roll_count, entry_test.entry_type)

    #print(iter_atk.die_roll_quant)
    #print(iter_atk.die_rolls_list)

    #print(atk_1.dx_result)
    #print(atk_2.effect_roll,atk_2.result_w_mods)

    #print(entries[1].roll_type)
    #print(entries[0].die_mods, entries[0].roll_type)
    #print(new_entry.die_mods)

    #new_entry.die_mods = 50

    #print(new_entry.die_mods)
main()