#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

# TODO 
# yeah, ok eventually you should probably accept that the first line of a real log doesn't start with hyphens 
# - how to specify type of saving throw when some don't specify? we'll have to pull from later lines to get that info. 
# - what kind of data type to hold a shitton of rolls? 
# - don't forget, you've fucked with the data in testslice.txt for testing purposes... FirstWorld.txt is the original, don't fuck with it
# finding nat 20s or 1s: look for the only roll line that has the = sign in it, and it should be the first integer to the right of the = 
# finding attacks: can we look for a line that has BOTH "attack" and "damage" in the line to start? that will give to hit and damage numbers. 
# attack keywords: attack, bite, slam, claw, wing 
# note that iterative attacks might be frustrating here: claws 2 # damage etc
# future attacks: Valeric's special macros and criticals
# theory: chat messages that are only 0-2 len are just like words we put in chat
# jump off find_roller to create characters or attribute a roll to an existing character? we should pass the whole roll to find_roller then
# another type of roll we've missed: drinking potions, look for keyword "(Drink)" so it doesn't get mixed up with someone just sharing a potion item to chat

from dataclasses import dataclass
import datetime
import pandas as pd

@dataclass
class roll():
    uid: int
    date: datetime
    roller: str
    type: int

class character():
    name: str
    savethrow_count: int

global src_file, roll_id, roller, roll_date, roll_id_flag, roll_type, roll_raws

def find_roller(txt):
    roller = txt.split("]")
    roller = roller[1].strip()

    return roller

def find_roll_date(txt): 
    # foundry formatted the dates like X/X/202X, XX:XX:XX.  
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

def find_roll_type(roll_lines):
    # TODO 
    # Differentiate saving throws if the system doesn't do that for us
    # Figure out attacks, spells/feature/item uses, initiative, concentration checks
    # count # of d20, d100s rolled 

    # roll_lines is a list where each string is a line of the roll. the first line is -s, then datetime and char rolling, then more information about the roll
    # types: 0 = untyped, 1 = initiative, 2 = level up report, 3 = saving throw, 4 = skill check, 5 = attack, 6 = spell/item/feature use 7 = raw 8 = error

    roll_id = roll_lines[2]
    roll_id_split = roll_id.split(" ")
    roll_type = 0 
    len_split = len(roll_id_split)
    saving_throw_type = ""
    skill_type = ""
    use_type = ""
    init_roll = 0.0

    for i in roll_id_split:
        match i:
            case "Saving" | "Throw": 
                roll_type = 3
                #roll_id_split.remove("Saving")
                #roll_id_split.remove("Throw")

                saving_throw_type = "Save"
                #saving_throw_type = roll_id_split[0]

            case "Concentration": 
                # what roll_type are we giving these? shoving into untyped since it's not handled yet
                roll_type = 0

            case "Skill": 
                roll_type = 4
                # now that we know it's a skill check, trim the list so only the type of skill check is left 
                roll_id_split.remove("Skill")
                roll_id_split.remove("Check")
                length = len(roll_id_split)
                if len(roll_id_split) > 1:
                    skill_type = find_skill_type(roll_id_split)
                else: 
                    skill_type = roll_id_split[0]

            case "(Use)":
                roll_type = 6
                roll_id_split.remove("(Use)")
                use_type = ' '.join(roll_id_split)

            case "Level" | "Up" | "Report":
                roll_type = 2

            case _:
                if roll_type > 0:
                    roll_type = roll_type  
                else: 
                    # okay, if i the first roll is a decimal or a number with a decimal point, then it's either initiative or raw (or untyped?)
                    init_list = i.split(".")
                    if len(init_list) > 1:
                        # if it's got a decimal point, that means it has a tiebreaker, so it's definitely initiative
                        roll_type = 1
                        init_roll = i
        
                    if i.isdecimal():
                        # some older initiatives didn't have tiebreakers yet, so we have to differentiate what kind of roll this is
                        # but initiative will be declared within the text of the roll so just take a peek
                        init_check = [x for x in roll_lines if x.startswith('Initiative')]
                        if init_check:
                            roll_type = 1
                            init_roll = i
                        else:
                            # OK, if it's not an initiative roll, it could be a raw roll. sometimes we just roll plain dice
                            # if that's the case, then the roll will be formatted like ---/[Datetime] Roller/Result/1dxx = xx = xx
                            # this is where we might count number of d20s or d100s rolled flat if we were so inclined 
                            # anyway so the raw rolls are only like 4 lines long, so len of the roll's list should give us that
                            if len(roll_lines) == 4:
                                roll_type = 7
                            else: 
                                roll_type = 8

                    if roll_type == 0:
                        # k if it's still not changed then we missed it and screwed up
                        roll_type = 8

    return roll_type, saving_throw_type, skill_type, use_type, init_roll

def find_skill_type(roll_id_list):
    skill_type = ""
    skill_length = len(roll_id_list)

    for i in roll_id_list:
        # rework how craft, knowledge, perform, profession checks are handled?
        match i:
            case "Acrobatics" | "Appraise" | "Bluff" | "Climb" | "Diplomacy" | "Disguise" | "Fly" | "Heal" | "Intimidate" | "Linguistics" | "Perception":
                skill_type = i
            case "Ride" | "Spellcraft" | "Stealth" | "Survival" | "Swim":
                skill_type = i
            case "Craft":
                skill_type = "Craft"
                roll_id_list.remove("Craft")
                skill_type = skill_type + " " + roll_id_list[0] 
            case "Disable" | "Device":
                skill_type = "Disable Device"
            case "Escape" | "Artist":
                skill_type = "Escape Artist"
            case "Handle" | "Animal":
                skill_type = "Handle Animal"
            case "Sleight" | "of" | "Hand":
                skill_type = "Sleight of Hand"
            case "Knowledge":
                skill_type = "Knowledge"
                roll_id_list.remove("Knowledge")
                skill_type = skill_type + " " + roll_id_list[0]
            case "Perform":
                skill_type = "Perform"
                roll_id_list.remove("Perform")
            case "Performance":
                skill_type = "Performance"
                roll_id_list.remove("Performance")
            case "Profession":
                skill_type = "Profession"
                roll_id_list.remove("Profession")
                skill_type = skill_type + " " + roll_id_list[0]
            case "Sense" | "Motive":
                skill_type = "Sense Motive"
            case "Use" | "Magic" | "Device":
                skill_type = "Use Magic Device"
            case "(New" | "Skill)" | "(Take" | "10)":
                roll_id_list.remove(i)
            case _:
                skill_type = skill_type + " " + i
                skill_type = skill_type.strip()

    return skill_type   

def roll_handler(roll_raws):
    # roll_id is the unique id for each item in roll_raws
    # each roll_id has a list of each line for a roll
    # the 0th string in the list is a bunch of --s 
    # the 1st string contains datetime and roller info
    # the 2nd string will be our primary identifier for type of roll 
    roll_id = len(roll_raws.keys())
    roll_stats = {
        roll_id: []
    }

    for id in roll_raws:
        roll_info = roll_raws[id]
        roller = find_roller(roll_info[1])
        roll_date = find_roll_date(roll_info[1])
        roll_type, saving_throw_type, skill_type, use_type, init_roll = find_roll_type(roll_info)
        roll_stats[id] = [roller, roll_date, roll_type, saving_throw_type, skill_type, use_type, init_roll]
        # print(roll_stats[id])
    return roll_stats

def pull_rolls(src_file):
    roll_id = 0 
    roll_raws = {
        roll_id: []
    }

    with open(src_file) as f:
        first_roll_flag = True 

        for line in f: 
            txt = line.strip()

            # if the first char of txt is - then it's a new roll 
            if txt.startswith("--"):
                if first_roll_flag == False:
                    roll_id += 1
                    roll_raws[roll_id] = [txt] 
                if first_roll_flag: 
                    first_roll_flag = False
                    roll_raws[roll_id].append(txt)
                                  
            else:
                roll_raws[roll_id].append(txt)       
                

    return roll_raws

def analyze_roll_stats(roll_stats):
    total_rolls = len(roll_stats.keys())
    # types: 0 = untyped, 1 = initiative, 2 = level up report, 3 = saving throw, 4 = skill check, 5 = attack, 6 = spell/item/feature use 7 = raw 8 = error
    init_rolled_count = 0
    levels_count = 0
    saves_count = 0
    skills_count = 0
    atks_count = 0
    use_count = 0 
    raw_count = 0
    untyped_count = 0
    error_count = 0
    error_ids = []

    for id in range(0,total_rolls-1):
        roll_info = roll_stats[id]
        roll_type = roll_info[2]
        match roll_type:
            case 0:
                untyped_count += 1
            case 1:
                init_rolled_count += 1
            case 2: 
                levels_count += 1
            case 3:
                saves_count += 1
            case 4:
                skills_count += 1
            case 5: 
                atks_count += 1
            case 6: 
                use_count += 1
            case 7:
                raw_count += 1
            case 8 | _:
                error_count += 1
                error_ids.append(id)


    rolls_by_type = [untyped_count, init_rolled_count, levels_count, saves_count, skills_count, atks_count, use_count, raw_count, error_count]
    
    return total_rolls, rolls_by_type, error_ids

def main():
    src_file = 'Data\TestSlice.txt'
    roll_id = 0
    roll_raws = {
        roll_id: []
    }

    # first, we pull the rolls from the text file into a dict 
    roll_raws = pull_rolls(src_file)

    # now that we've got the data pulled out, let's call roll handler 
    # roll handler is going to return information about the rolls
    # for now let's try to get datetime, roller, and roll type
    roll_stats = roll_handler(roll_raws)

    # let's get some stats just because
    total_rolls, rolls_by_type, error_ids = analyze_roll_stats(roll_stats)
    print("Total rolls: ", total_rolls)
    print("Rolls by type: Untyped, Initiative, Level Ups, Saving Throws, Skill Checks, Attacks, Spells/Class Features/Items Used, Raw, Error")
    print(rolls_by_type)

    #for id in error_ids:
       # print(roll_raws[id])


main()