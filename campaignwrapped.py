#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

# TODO 
# Finish class refactor 
# Separate this file out into a couple different files cos this is getting long and annoying. one file for classes, one for roll identification? 
# how to differentiate different campaigns so we don't end up putting multiple campaigns in the gamemaster bucket? 

import datetime
import os
import roll_identification
import classes

global src_file

def log_handler(log_bin, this_campaign): 
    for log in log_bin:
        log.date_time = roll_identification.find_roll_date(log.log_lines)
        log.actor = roll_identification.find_actor(log.log_lines)
        roll_identification.initialize_roll(log)
        if log.actor in this_campaign.list_player_actors():
            actor_obj = this_campaign.fetch_actor(log.actor)
            actor_obj.add_log(log)
        else:
            # this is where we figure out if this log belongs to a different campaign or the gm 
            # first let's just assign it to the gm 
            print(log.actor)
    return log_bin

def pull_log_lines(src_file):
    log_bin = []
    log_lines = []
    first_line_flag = True
    default_datetime = (1900, 1, 1)
    default_actor = "Actor Unknown"

    with open(os.path.join(os.path.dirname(__file__), src_file), 'r') as input_file:
        for line in input_file: 
            txt = line.strip()

            # if it's our first roll there won't be -- before it
            if first_line_flag: 
                log_lines.append("---------------------------")
                first_line_flag = False

            # if the first char of txt is - then it's a new roll 
            if txt.startswith("--"):
                # make log entry object with previous list of strings, then start the next list
                log_bin.append(classes.log_entry(default_datetime, default_actor, log_lines, ""))
                log_lines = [txt]                     
            else:
                log_lines.append(txt)       

    input_file.close()
    return log_bin

def main():
    src_file = "data/FirstWorld_Mod.txt"

    log_bin = []

    one_campaign = classes.campaign("Hell's Rebels", ["H1", "Z1", "D1", "M1"])
    one_campaign.update_player_actor("Z1", ["Namielle", "Ercia Kash"])
    one_campaign.update_player_actor("H1",["Valeric"])
    one_campaign.update_player_actor("D1", ["Gage"])
    one_campaign.update_player_actor("M1", ["Tihana"])
    one_campaign.update_player_actor("Gamemaster",["Goblin", "Orc", "Dragon"])
    one_campaign.show_player_stats()

    log_bin = pull_log_lines(src_file)
    log_bin = log_handler(log_bin, one_campaign)

    one_campaign.show_player_stats()
    '''
    for i in range(0, len(log_bin)):
        if log_bin[i].roll_count > 1:
            print(log_bin[i].entry_type)
        if log_bin[i].actor == "Namielle":
            #print(log_bin[i].entry_type, log_bin[i].actor, "threw a", log_bin[i].roll_bin[0].dx_result)
            char1.add_log(log_bin[i])
        if log_bin[i].actor == "Gage":
            char2.add_log(log_bin[i])
  
   for i in range (0, char1.logs_count):
       if char2.logs_bin[i].entry_type == "Initiative":
            print(char2.logs_bin[i].actor, "threw a", char2.logs_bin[i].roll_bin[0].dx_result)
    print(char1.name, "threw", char1.nat_one_count, "natural 1s and", char1.nat_twenty_count, "natural 20s and", 
          char1.nat_hundred_count, "natural hundreds, out of", char1.roll_count, "total rolls")
    print(char2.name, "threw", char2.nat_one_count, "natural 1s and", char2.nat_twenty_count, "natural 20s and", 
          char2.nat_hundred_count, "natural hundreds out of", char2.roll_count, "total rolls")

    '''
main()

