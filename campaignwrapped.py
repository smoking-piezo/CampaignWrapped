#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

from dataclasses import dataclass
import datetime
#import pandas as pd

global src_file

@dataclass
class player():
    def add_actor(self, actor_name):
        actor_exists = isinstance(actor_name, actor)
        if actor_exists:
            if actor_name not in self.actors_list:
                self.actors_list.append(actor_name)
        else:
            pass
        return self.actors_list
        
    def __init__(self, name, campaigns_list, actors_list):
        self.actors_list = []
        self.name = name
        self.campaigns_list = campaigns_list
        for actor_name in range(0, len(actors_list)):
            self.add_actor(actors_list[actor_name])
            
class actor():
    def add_log(self, log_entry):
        if self.logs_bin:
            self.logs_bin.append(log_entry)
        else:
            self.logs_bin = [log_entry]
        self.logs_count = len(self.logs_bin)
        self.roll_count = self.roll_count + log_entry.roll_count

        if log_entry.nat_one_count: 
            self.nat_one_count += log_entry.nat_one_count
        if log_entry.nat_twenty_count:
            self.nat_twenty_count += log_entry.nat_twenty_count
        if log_entry.nat_hundred_count:
            self.nat_hundred_count += log_entry.nat_hundred_count
        return self.logs_bin, self.logs_count, self.roll_count, self.nat_one_count, self.nat_twenty_count, self.nat_hundred_count

    def __init__(self, name, player, logs_bin=[]):
        self.name = name
        self.player = player 
        self.logs_bin = logs_bin
        logs_count = len(logs_bin)
        if logs_count > 0:
            for i in range(0,logs_count): 
                roll_count += logs_bin[i].roll_count
        else:
            roll_count = 0
        self.roll_count = roll_count
        self.nat_one_count = 0
        self.nat_twenty_count = 0
        self.nat_hundred_count = 0

class log_entry():
    acceptable_types = ["Unknown", "Initiative", "Level Up", "Will Saving Throw", "Reflex Saving Throw", 
                        "Fortitude Saving Throw", 'Unknown Saving Throw', "Skill Check", "Attack",
                        "Spell Cast", "Item / Potion Used", "Raw Roll", "Chat Message", "Ability Test",
                        "Combat Maneuver", "Caster Level Check", "Defenses", "Error"]
    
    def add_roll(self, roll_object):
        if self.roll_bin:
            self.roll_bin = self.roll_bin.append(roll_object)
        else:
            self.roll_bin = [roll_object]
        self.roll_bin = self.roll_bin
        self.roll_count = len(self.roll_bin)

        if roll_object.nat_one_flag:
            self.nat_one_count += 1
        if roll_object.nat_twenty_flag:
            self.nat_twenty_count += 1
        if roll_object.nat_hundred_flag:
            self.nat_hundred_count += 1

        return self.roll_bin, self.roll_count, self.nat_one_count, self.nat_twenty_count, self.nat_hundred_count
    
    def update_type(self, roll_type):
        if roll_type in self.acceptable_types:
            self.entry_type = roll_type
        elif roll_type:
            self.entry_type = "Error"
        else: 
            self.entry_type = "Unknown"
        return self.entry_type

    def __init__(self, date_time, actor, log_lines, entry_type, roll_bin=[]):
        self.date_time = date_time
        self.actor = actor
        self.log_lines = log_lines 
        self.roll_bin = roll_bin
        self.roll_count = len(roll_bin)
        self.nat_one_count = 0
        self.nat_twenty_count = 0
        self.nat_hundred_count = 0
        if entry_type in self.acceptable_types:
            self.entry_type = entry_type
        elif entry_type:
            self.entry_type = "Error"
        else: 
            self.entry_type = "Unknown"

class die_roll():
    def __init__(self, dx_type, dx_result, result_w_mods=0):
        self.dx_type = dx_type
        self.dx_result = dx_result
        if result_w_mods:
            self.result_w_mods = result_w_mods
        else: 
            self.result_w_mods = dx_result

        self.nat_one_flag, self.nat_twenty_flag, self.nat_hundred_flag = self.notable_rolls(dx_type, dx_result)
    
    def notable_rolls(self, dx_type, dx_result):
        nat_one_flag = False
        nat_twenty_flag = False
        nat_hundred_flag = False

        if dx_result == 1:
            nat_one_flag = True
        
        if dx_result == 20 and dx_type == "d20":
            nat_twenty_flag = True
        
        if dx_result == 100 and dx_type == "d100":
            nat_hundred_flag = True

        return nat_one_flag, nat_twenty_flag, nat_hundred_flag

def find_actor(log_lines):
    txt = log_lines[1]
    actor = txt.split("]")
    actor = actor[1].strip()

    return actor

def find_roll_date(log_lines): 
    # Date is found in the 1st line of the roll, formatted line  [X/X/202X, XX:XX:XX] Roller_Name  
    txt = log_lines[1]
    month_str_pos = txt.rfind("/", 0, 4)
    month = int(txt[1:month_str_pos])

    day_str_pos = txt.rfind("/", month_str_pos, 10)
    day = int(txt[month_str_pos+1:day_str_pos])

    year_str_pos = txt.rfind("/", day_str_pos, 15)
    year = int(txt[year_str_pos+1:year_str_pos+5])

    hour_str_pos_start = int(txt.index(","))+1
    hour_str_pos_end = int(txt.index(":"))
    hour =int(txt[hour_str_pos_start:hour_str_pos_end])

    min_str_pos_start = hour_str_pos_end+1
    min_str_pos_end = hour_str_pos_end+3
    min = int(txt[min_str_pos_start:min_str_pos_end])

    sec_str_pos_start = min_str_pos_end+1
    sec_str_pos_end = sec_str_pos_start+2
    sec = int(txt[sec_str_pos_start:sec_str_pos_end])

    roll_date = datetime.datetime(year, month, day, hour, min, sec)

    return roll_date

def initialize_roll(log):
    # so initially this function was just intended to find the TYPE of roll in the log, but 
    # now I think we need to also initialize the roll fully. which is to say: 
    # make sure all the dice objects associated with a roll are loaded into the log entry 
    roll_id = log.log_lines[2]
    roll_id_split = roll_id.split(" ")
    roll_lines = log.log_lines

    attack_keywords = ["Attack", "Claw", "Wing", "Bite", "Slam", "2nd Claw", "Thwack"]
    save_keywords = ["Fortitude", "Reflex", "Will", "Saving Throw"]
    show_keywords = ["School", "Source", "Description", "Price"]

    init_check = [line for line in log.log_lines if line.startswith('Initiative')]
    if init_check: 
        init_init_roll(log)
        return 
    
    for keyword in roll_id_split:
        match keyword:
            case "Saving" | "Throw":
                init_save_roll(log)
                return
            case _:
                return
        '''
            case "Concentration":
                init_generic_roll(log, "Concentration Check")
            case "Skill":
                init_skill_check(log)
            case "(Use)" | "(Drink)":
                init_use_save_roll(log)
            case "Up" | "Report"
                init_level_up(log)
            case "Ability" | "Test": 
                init_generic_roll(log, "Ability Test")
            case "Melee" | "Ranged":
                init_attack(log)
            case "Caster":
                init_generic_roll(log, "Caster Level Check")
            case "Defenses":
                init_message(log)

    for line in range(0, len(roll_lines)):
        attack_check = any(roll_lines[line].startswith(keyword) for keyword in attack_keywords)
        show_check = any(roll_lines[line].startswith(keyword) for keyword in show_keywords)
        
        if attack_check:
            init_attack(log)
            return 
        
        if show_check:
            init_message(log)
    '''

def init_save_roll(log):
    roll_lines = log.log_lines
    roll_id = roll_lines[2]
    roll_len = len(roll_lines)
    save_keywords = ["Constitution", "Dexterity", "Wisdom"]
    saving_throw_type = ""
    i = 0

    if roll_id.startswith("Saving"):
        # if it starts with "Saving Throw" then we need to figure out what kind of save it is from other clues
        for i in range(0,roll_len):
            # the below line is NOT catching the lines it should be 
            save_check = any(roll_lines[i].startswith(keyword) for keyword in save_keywords)
            if save_check:
                save_type = roll_lines[i].split(" ")
                save_type = save_type[0]
                break
            else:
                save_type = "Other"

        match save_type:
            case "Constitution":
                saving_throw_type = "Fortitude Saving Throw"
            case "Dexterity":
                saving_throw_type = "Reflex Saving Throw"
            case "Wisdom":
                saving_throw_type = "Will Saving Throw"
            case _:
                saving_throw_type = "Unknown Saving Throw"
    else:
        saving_throw_type = roll_id

    dx_type = "d20"

    # in the old log some of the early result lines got messed up and only the modified result is available 
    # but the d20 roll is still there, just on a different line than expected 
    dx_result_line = [line for line in roll_lines if line.startswith('1d20')]
    dx_result_line = dx_result_line[0].split(" ")
    dx_result = int(dx_result_line[1].strip())

    mod_result_line = [line for line in roll_lines if "=" in line]
    mod_result_line = mod_result_line[0].split("=")
    result_w_mods = int(mod_result_line[2].strip())

    save_roll = die_roll(dx_type, dx_result, result_w_mods)

    log.update_type(saving_throw_type)
    log.add_roll(save_roll)
    
    return


def init_init_roll(log):
    # to initialize an initiative roll, we need to get the associated dice roll 
    # this will probably be in the last line which starts with 1d20
    # we want to add the d20 roll and the result roll with modifiers 

    result_line = [line for line in log.log_lines if line.startswith('1d20') and "=" in line]

    result_line = result_line[0].split("=")

    dx_type = "d20"
    split_result_line = result_line[1].split("+")
    dx_result = int(split_result_line[0].strip())
    result_w_mods = float(result_line[2])

    init_roll = die_roll(dx_type, dx_result, result_w_mods)

    log.update_type("Initiative")
    log.add_roll(init_roll)
    
    return

def log_handler(log_bin): 
    for log in log_bin:
        log.date_time = find_roll_date(log.log_lines)
        log.actor = find_actor(log.log_lines)
        # return something here? 
        initialize_roll(log)

    return log_bin

def pull_log_lines(src_file):
    log_bin = []
    log_lines = []
    first_line_flag = True
    default_datetime = (1900, 1, 1)
    default_actor = "Actor Unknown"

    with open(src_file) as f:
        for line in f: 
            txt = line.strip()

            # if it's our first roll there won't be -- before it
            if first_line_flag: 
                log_lines.append("---------------------------")
                first_line_flag = False

            # if the first char of txt is - then it's a new roll 
            if txt.startswith("--"):
                # make log entry object with previous list of strings, then start the next list
                log_bin.append(log_entry(default_datetime, default_actor, log_lines, ""))
                log_lines = [txt]                     
            else:
                log_lines.append(txt)       
    return log_bin

def main():
    #src_file = 'Data\TestSlice.txt'
    log_bin = []

    log_bin = pull_log_lines(src_file)
    log_bin = log_handler(log_bin)

    player1 = player("Z1", ["Hell's Rebels", "Iron Gods", "Ruins of Azlant"], ["Namielle", "Ercia Kash"])
    char1 = actor("Namielle", "Z1")
    char2 = actor("Gage", "D1")

    for i in range(0, len(log_bin)):
        if log_bin[i].roll_count > 1:
            print(log_bin[i].entry_type)
        if log_bin[i].actor == "Namielle":
            #print(log_bin[i].entry_type, log_bin[i].actor, "threw a", log_bin[i].roll_bin[0].dx_result)
            char1.add_log(log_bin[i])
        if log_bin[i].actor == "Gage":
            char2.add_log(log_bin[i])
            
  
   # for i in range (0, char1.logs_count):
       # if char2.logs_bin[i].entry_type == "Initiative":
            #print(char2.logs_bin[i].actor, "threw a", char2.logs_bin[i].roll_bin[0].dx_result)
    print(char1.name, "threw", char1.nat_one_count, "natural 1s and", char1.nat_twenty_count, "natural 20s and", char1.nat_hundred_count, "natural hundreds")
    print(char2.name, "threw", char2.nat_one_count, "natural 1s and", char2.nat_twenty_count, "natural 20s and", char2.nat_hundred_count, "natural hundreds")

main()
