#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

from dataclasses import dataclass
import datetime
#import pandas as pd

global src_file, roll_id, roller, roll_date, roll_id_flag, roll_type, roll_raws

@dataclass

class log_entry():
    acceptable_types = ["Unknown", "Initiative", "Level Up", "Saving Throw", "Skill Check", "Attack",
                        "Spell Cast", "Item / Potion Used", "Raw Roll", "Chat Message", "Ability Test",
                        "Combat Maneuver", "Caster Level Check", "Defenses", "Error"]
    
    def add_roll(self, roll_object):
        if self.roll_bin:
            self.roll_bin = self.roll_bin.append(roll_object)
        else:
            self.roll_bin = [roll_object]
        self.roll_bin = self.roll_bin
        self.roll_count = len(self.roll_bin)
        return self.roll_bin

    def __init__(self, date_time, actor, log_lines, entry_type, roll_bin=[]):
        self.date_time = date_time
        self.actor = actor
        self.log_lines = log_lines 
        self.roll_bin = roll_bin
        self.roll_count = len(roll_bin)
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
    roll_lines = log.log_lines

    attack_keywords = ["Attack", "Claw", "Wing", "Bite", "Slam", "2nd Claw", "Thwack"]
    save_keywords = ["Fortitude", "Reflex", "Will", "Saving Throw"]
    show_keywords = ["School", "Source", "Description", "Price"]


    init_check = [line for line in log.log_lines if line.startswith('Initiative')]
    if init_check: 
        roll_type = "Initiative"
        init_init_roll(log)
        return 
    
    for line in range(0, len(roll_lines)):
        attack_check = any(roll_lines[line].startswith(keyword) for keyword in attack_keywords)
        save_check = any(roll_lines[line].startswith(keyword) for keyword in save_keywords)
        
        if attack_check:
            roll_type = "Attack"
            return 
        
        if save_check: 
            roll_type = "Saving Throw" 
            return

    return

def init_init_roll(log):
    # to initialize an initiative roll, we need to get the associated dice roll 
    # this will probably be in the last line which starts with 1d20
    # we want to add the d20 roll and the result roll with modifiers 

    roll_lines = log.log_lines
    result_line = [line for line in log.log_lines if line.startswith('1d20') and "=" in line]

    result_line = result_line[0].split("=")


    dx_type = "d20"
    split_result_line = result_line[1].split("+")
    dx_result = int(split_result_line[0].strip())
    result_w_mods = float(result_line[2])

    init_roll = die_roll(dx_type, dx_result, result_w_mods)

    log.entry_type = "Initiative"
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
    src_file = 'Data\TestSlice.txt'
    log_bin = []

    log_bin = pull_log_lines(src_file)
    log_bin = log_handler(log_bin)

    #for i in range(0, len(log_bin)):
        #print(log_bin[i].entry_type, log_bin[i].roll_count)


main()