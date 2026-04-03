#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

# TODO 
# how are we gonna handle tallying up the types of skill checks by skill types? 
# differentiate campaigns by date/character?

import datetime
import os
import roll_identification
import classes

global src_files

def log_handler(log_bin, campaigns_bin): 
    for log in log_bin:
        log.date_time = roll_identification.find_roll_date(log.log_lines)
        log.actor = roll_identification.find_actor(log.log_lines)
        roll_identification.initialize_roll(log)
        for this_campaign in campaigns_bin:
            if log.actor in this_campaign.list_player_actors():
                actor_obj = this_campaign.fetch_actor(log.actor)
                actor_obj.add_log(log)
        #else:
            # this is where we figure out if this log belongs to a different campaign or the gm 
            # okay, what if we created all the campaigns in a list passed to the log handler 
            # if it's not in the list_player_actors, pick a known PC from that campaign and get the most recent roll date
            # if the roll date matches, but it doesn't match a PC, then let's assign it to that campaign's GM 

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

def return_dates(log_entry):
    return log_entry.date_time

def main():
    src_file = "data/FirstWorld_Mod.txt"

    log_bin = []

    hells_rebels = classes.campaign("Hell's Rebels", ["H1", "Z1", "D1", "M1"])
    hells_rebels.update_player_actor("Z1", ["Namielle", "Ercia Kash"])
    hells_rebels.update_player_actor("H1",["Valeric"])
    hells_rebels.update_player_actor("D1", ["Gage"])
    hells_rebels.update_player_actor("M1", ["Tihana"])

    iron_gods = classes.campaign("Iron Gods", ["H1", "Z1", "D1", "M1"])
    iron_gods.update_player_actor("H1", ["Construct", "Harnok"])
    iron_gods.update_player_actor("Z1", ["Sassiel GreeTrink"])
    iron_gods.update_player_actor("D1", ["Rory"])
    iron_gods.update_player_actor("M1", ["Verna", "Irontrunk", "Hazal/Verna/Suvi/Talvi"])
    
    ruins_azlant = classes.campaign("Ruins of Azlant", ["H1", "Z1", "D1", "M1"])
    ruins_azlant.update_player_actor("H1", ["Garzu"])
    ruins_azlant.update_player_actor("Z1", ["Kurina"])
    ruins_azlant.update_player_actor("D1", ["Kazell"])
    ruins_azlant.update_player_actor("M1", ["Mavuto"])

    campaigns_bin = [hells_rebels, iron_gods, ruins_azlant]

    log_bin = pull_log_lines(src_file)
    log_bin = log_handler(log_bin, campaigns_bin)

    hells_rebels.show_player_stats("D1")
    iron_gods.show_player_stats("M1")

    gage = hells_rebels.fetch_actor("Gage")

    hells_rebels_dates = filter(return_dates, gage.logs_bin)

main()