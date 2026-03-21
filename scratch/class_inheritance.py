#! python 3 

from dataclasses import dataclass
import datetime

@dataclass
class log_entry():
    def __init__(self, date_time, roller, log_lines):
        self.date_time = date_time
        self.roller = roller
        self.log_lines = log_lines 

class dice_roll(log_entry):

    def __init__(self, date_time, roller, log_lines, roll_type="Unknown"):
        super().__init__(date_time, roller, log_lines)
        if roll_type:
            self.roll_type = roll_type



def main():
    log = [["------","(2020, 10, 10)","roller name","stealth skill check", "30", "d20 + mods = 15 + 15", "very sneak"],["-------","(2010,12,15)","another roller","attack", "attack 20 damage 15","pew pew"]]
    entries = []

    for i in range(0,2):
        entry_date = log[i][1]
        entry_roller = log[i][2]
        entry_log = log[i]
        entries.append(log_entry(entry_date,entry_roller,entry_log))

    entries[1]=dice_roll(entries[1].date_time, entries[1].roller,entries[1].log_lines, "Attack")

    print(entries[1].roll_type)

main()
