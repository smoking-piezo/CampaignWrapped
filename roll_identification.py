#! python3
# roll_identification.py 
# These are Campaign Wrapped's roll-identifying functions. 

import datetime, classes

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
        init_generic_roll(log, "Initiative")
        return 
    
    # if an actor "Took 10" or "Took 20" on a skill or other check then it'll show up in the roll_id line
    # that'll cause an error, so let's trim that out 
    keywords_to_remove = ["(Take", "10)", "20)"]
    present_removable_keywords = []

    for index in range(0, len(roll_id_split)):
        for removable_keyword in keywords_to_remove:
            if roll_id_split[index] == removable_keyword:
                # we can't just straight up remove the keywords from the list WHILE we're iterating through it or we get an index error
                # so we make a list of the words that are in the roll_id and remove them later
                # there's gotta be a better way to do this than ANOTHER for loop? oh well
                present_removable_keywords.append(removable_keyword)

    for each in present_removable_keywords:
        roll_id_split.remove(each)  
    # ok, now that we've done this, we have to pass it to whatever init function the roll goes to so we don't get this same error 
    
    for keyword in roll_id_split:
        match keyword:
            case "Saving" | "Throw":
                init_save_roll(log, roll_id_split)
                break
            case "Concentration":
                init_generic_roll(log, "Concentration Check")
                break
            case "Ability" | "Test": 
                init_generic_roll(log, "Ability Test")
                break
            case "Caster":
                init_generic_roll(log, "Caster Level Check")
                break
            case "Combat" | "Maneuver" | "Bonus": 
                init_generic_roll(log, "Combat Maneuver Bonus")
                break
            case "Skill":
                init_generic_roll(log, "Skill Check")
                break
            case "(Use)" | "(Drink)":
                init_use_roll(log, keyword)
            case _:
                continue
        #print(keyword)
    return
    '''
            case "(Use)" | "(Drink)":
                init_use_save_roll(log)
            case "Up" | "Report"
                init_level_up(log)
            case "Melee" | "Ranged":
                init_attack(log)

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

def init_generic_roll(log, roll_type):
    # a generic roll is a type of roll that has a type attached to it, a single d20 roll, and not much else
    # the following types of rolls will be handled: Concentration Checks, Ability Test, Caster Level Check, CMB/CMD

    # to initialize a roll, we need to get the associated dice roll. this will probably be in the last line which starts with "1d20"
    # we want to add the d20 roll and the result roll with modifiers 
    # however, some of the older logs have an issue where the final line is missing information, so it'll be " =  = resultwmods"
    # so we'll have to look for the OTHER line in the roll that starts with "1d20" and pick out the second string in the split 

    dx_type = "d20"
    result_line = [line for line in log.log_lines if line.startswith('1d20') and "=" in line]

    try: 
        result_line = result_line[0].split("=")

    except IndexError:
        # OK so if we're here, then we're at an old log. now we need to look at the log_lines:
        # log_lines[3] will have the full roll, and the line after will start with 1d20 and give the roll
        result_w_mods = int(log.log_lines[3])
        result_line = [line for line in log.log_lines if line.startswith('1d20') and "=" not in line]
        split_result_line = result_line[0].split(" ")
        dx_result = split_result_line[1]

    else: 
        split_result_line = result_line[1].split("+")
        dx_result = int(split_result_line[0].strip())
        if roll_type == "Initiative":
            result_w_mods = float(result_line[2])
        else:
            result_w_mods = int(result_line[2])
    

    roll_obj = classes.die_roll(dx_type, dx_result, result_w_mods)
    
    log.update_type(roll_type)
    log.add_roll(roll_obj)

    return 

def init_save_roll(log, roll_id_split):
    roll_lines = log.log_lines
    roll_id = ' '.join(roll_id_split)
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

    log.update_type(saving_throw_type)
    log.add_roll(classes.die_roll(dx_type,dx_result,result_w_mods))
    
    return

def init_use_roll(log, keyword):
    # this roll is either an item usage, a class feature usage, OR a spell cast 
    
    # if (Drink) is in the roll_id then it means a potion was drunk and we're just gonna call that an item use
    # there MAY be a roll associated with the potion usage depending on the type of potion 
    # a cure potion will have a line that says "healing X" but it only gives the result in X. there are likely more cases of this
    if keyword == "(Drink)":
        roll_type = "Item Used"

    # otherwise the keyword was (Use) and we gotta figure out how to figure out if this is an item, a spell, or a class feature
    # maybe we find a way to import the reference compendiums and search em? 