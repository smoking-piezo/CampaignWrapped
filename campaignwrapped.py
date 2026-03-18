#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

# TODO 
# what kind of data type to hold a shitton of rolls? 
# upload an anyonyized chat log dataset
# finding nat 20s or 1s: look for the only roll line that has the = sign in it, and it should be the first integer to the right of the = 
# note that iterative attacks might be frustrating here: claws 2 # damage etc
# jump off find_roller to create characters or attribute a roll to an existing character? we should pass the whole roll to find_roller then
# potential error: foundry stopped formatting the d20 roll properly here?? 9/26/2022, 8:28:50 PM


from dataclasses import dataclass
import datetime
#import pandas as pd

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
    # Date is found in the 1st line of the roll, formatted line  [X/X/202X, XX:XX:XX] Roller_Name  
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

    # roll_lines is a list where each string is a line of the roll. the 0th line is hyphens, then 1st is datetime and char rolling, then 3rd is more information about the roll
    # while many types of rolls can be figured out easily from the 3rd line, some are more variable. initiative and raw rolls can look the same, and attacks are inconsistent
    # we'll figure out initiative and attacks from context clues on other lines
    # raw rolls will be 4 lines long (--, [date, time] roller, roll result, dxxx calculation)
    # chat lines will be 3 lines long (--, [date, time] roller, chat text)
    # types: 0 = untyped, 1 = initiative, 2 = level up report, 3 = saving throw, 4 = skill check, 5 = attack, 6 = spell/item/feature use, 7 = raw, 8 = chat, 9 = concentration, 10 = ability test
    # 11 = combat maneuver, 12 = melee attack, 13 = ranged attack, 14 = caster level check, 15 = showoff, 16 = error 
    
    roll_len = len(roll_lines)
    roll_id = roll_lines[2]
    roll_id_split = roll_id.split(" ")
    roll_type = 0 
    save_check = ""
    saving_throw_type = ""
    skill_type = ""
    use_type = ""
    init_roll = 0.0
    attack_keywords = ["Attack", "Claw", "Wing", "Bite", "Slam", "2nd Claw", "Thwack"]
    save_keywords = ["Constitution", "Dexterity", "Wisdom"]
    show_keywords = ["School", "Source", "Description"]
    count_clc = 0

    init_check = [line for line in roll_lines if line.startswith('Initiative')]
    if init_check:
        roll_type = 1
        # okay, looks like in 2024 Foundry changed how they were formatting initiative rolls on us, so we adjust accordingly
        #if(roll_id == "Initiative"):
            # double-check this typing here
           # init_roll = roll_lines[3]
        #else:
            #init_roll = float(roll_id)
        # figure out d20 roll 

    for i in range (0, roll_len):
        # note that while the actual attack roll itself may not start with "Attack" or it may start with "Weapon", there IS a line in most attacks that starts with the word "Attack" SOMEWHERE in the roll
        attack_check = any(roll_lines[i].startswith(keyword) for keyword in attack_keywords)
        if attack_check:
            roll_type = 5
            # go to some sort of attack-figuring out function ig
            exit

    match roll_len:
        case 3:
            # this may be a chat message 
            roll_type = 8 
        case 4:
            # this may be a raw roll
            if(roll_id.isdecimal()):
                roll_type = 7
        case _:
            roll_type = roll_type
    
    if roll_type == 0:
        for i in roll_id_split:
            match i:
                case "Saving" | "Throw": 
                    roll_type = 3
                    roll_id_split.remove("Saving")
                    roll_id_split.remove("Throw")

                    if len(roll_id_split) == 0:
                        # if there's nothing left in the roll_id_split then we've found an old saving throw that doesn't specify and we have to figure it out
                        # a Fortitude save will include mention of the roller's Constitution; Reflex, their Dexterity; and Will, their Wisdom 
                    
                        for i in range(0,roll_len):
                            save_check = any(roll_lines[i].startswith(keyword) for keyword in save_keywords)
                            if save_check:
                                save_type = roll_lines[i].split(" ")
                                save_type = save_type[0]
                                exit
                            else:
                                save_type = "Other"

                        match save_type:
                            case "Constitution":
                                saving_throw_type = "Fortitude"
                            case "Dexterity":
                                saving_throw_type = "Reflex"
                            case "Wisdom":
                                saving_throw_type = "Will"
                            case _:
                                saving_throw_type = "Save"
                    else: 
                        saving_throw_type = roll_id_split
                    
                case "Concentration": 
                    roll_type = 9

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

                case "(Use)" | "(Drink)":
                    roll_type = 6
                    if i == "(Use)":
                        roll_id_split.remove("(Use)")
                    else: 
                        roll_id_split.remove("(Drink)")
                    use_type = ' '.join(roll_id_split)

                case "Up" | "Report":
                    roll_type = 2

                case "Ability" | "Test":
                    roll_type = 10

                case "Combat" | "Maneuver" | "Bonus": 
                    roll_type = 11
                    # need to check if CMB or CMD? 
                
                case "Melee":
                    roll_type = 12
                
                case "Ranged":
                    roll_type = 13
                
                case "Caster":
                    roll_type = 14
                    #count_clc += 1
                case _:
                    if roll_type == 0:
                        for i in range(0, roll_len):
                            show_check = any(roll_lines[i].startswith(keyword) for keyword in show_keywords)
                            if show_check:
                                roll_type = 15
                                exit
                    if roll_type == 0:
                        roll_type = 16
    
    #if count_clc:
        #print(roll_id, roll_type)
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
    roll_id = 0
    roll_stats = {
        roll_id: []
    }

    for id in roll_raws:
        roll_info = roll_raws[id]
        roller = find_roller(roll_info[1])
        roll_date = find_roll_date(roll_info[1])
        roll_type, saving_throw_type, skill_type, use_type, init_roll = find_roll_type(roll_info)
        roll_stats[id] = [roller, roll_date, roll_type, saving_throw_type, skill_type, use_type, init_roll]
    return roll_stats

def pull_rolls(src_file):
    roll_id = 0 
    roll_raws = {
        roll_id: []
    }
    first_line_flag = True

    with open(src_file) as f:
        for line in f: 
            txt = line.strip()

            # if it's our first roll there won't be -- before it
            if roll_id == 0 and first_line_flag: 
                roll_raws[roll_id].append("---------------------------")
                first_line_flag = False

            # if the first char of txt is - then it's a new roll 
            if txt.startswith("--"):
                roll_id += 1
                roll_raws[roll_id] = [txt]                     
            else:
                roll_raws[roll_id].append(txt)       
    return roll_raws

def analyze_roll_stats(roll_stats):
    total_rolls = len(roll_stats.keys())-1
    # types: 0 = untyped, 1 = initiative, 2 = level up report, 3 = saving throw, 4 = skill check, 5 = attack, 6 = spell/item/feature use, 7 = raw, 8 = chat, 9 = concentration, 10 = ability test
    # 11 = combat maneuver, 12 = melee attack, 13 = ranged attack, 14 = caster level check, 15 = error 
    init_rolled_count = 0
    levels_count = 0
    saves_count = 0
    skills_count = 0
    atks_count = 0
    use_count = 0 
    raw_count = 0
    untyped_count = 0
    chat_count = 0
    conc_count = 0
    ability_count = 0 
    combman_count = 0
    melee_count = 0
    ranged_count = 0
    clc_count = 0
    show_count = 0
    error_count = 0
    error_ids = []

    for id in range(0,total_rolls):
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
            case 8:
                chat_count += 1
            case 9:
                conc_count += 1 
            case 10:
                ability_count += 1
            case 11:
                combman_count += 1
            case 12:
                melee_count += 1
            case 13:
                ranged_count += 1
            case 14:
                clc_count += 1
            case 15:
                show_count += 1
            case 16 | _:
                error_count += 1
                error_ids.append(id)
    sum_count = untyped_count + init_rolled_count + levels_count + saves_count + skills_count + atks_count + use_count + raw_count + chat_count 
    sum_count = sum_count + conc_count + ability_count + combman_count + melee_count + ranged_count + clc_count + error_count

    rolls_by_type = [untyped_count, init_rolled_count, levels_count, saves_count, skills_count, atks_count, use_count, raw_count, chat_count, 
                     conc_count, ability_count, combman_count, melee_count, ranged_count, clc_count, show_count, error_count]
    
    return total_rolls, rolls_by_type, error_ids

def main():
    # fix this line 
    src_file = ''
    roll_id = 0
    roll_raws = {
        roll_id: []
    }

    # first, we pull the rolls from the text file into a dict 
    roll_raws = pull_rolls(src_file)
    #print(len(roll_raws))

    # now that we've got the data pulled out, let's call roll handler 
    # roll handler is going to return information about the rolls
    # for now let's try to get datetime, roller, and roll type
    roll_stats = roll_handler(roll_raws)
    #print(len(roll_stats))

    # let's get some stats just because
    roll_types = ["Untyped", "Initiative", "Level Up", "Saving Throw", "Skill Check", "Attack", "Spell/Class Feat/Item Used", "Raw Roll", "Chat Message", 
                  "Concentration Check", "Ability Test", "Combat Maneuver", "Melee Attack", "Ranged Attack", "Caster Level Check", "Showoff", "Error"]
    total_rolls, rolls_by_type, error_ids = analyze_roll_stats(roll_stats)
    print("Total rolls: ", total_rolls)
    sum_total = 0
    for i in range(0,len(roll_types)):
        sum_total += rolls_by_type[i]
        print(roll_types[i], rolls_by_type[i])
        i+=1
    print("Total rolls: ", sum_total)

    for id in error_ids:
        print(roll_raws[id])


main()
