#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

# TODO 
# how are we gonna handle tallying up the types of skill checks by skill types? 
# differentiate campaigns by date/character?
# correct the campaign class's show player stats function to utilize the player class's function instead 
# for the log handler function, it doesn't really matter if they're NPCs or PCs. we know which ones are PCs. so let's flatten that logic into one list

# remove roll from data file dated [1/8/2024, 8:09:05 PM] Boris
# those rolls where Harnok DMed the GM about silver in Hell's Rebels and the program later changed his actor name to Construct? Change the name to Harnok. because it's screwing us up 
# Harnok's roll on 1/8/24 - change to Construct - actually there's a few to correct 
# remove Irontrunk roll 9/29/23? 

import datetime as dt
import os
import roll_identification, classes, campaign_log_filter

def pull_logs(src_file):
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

    for log in log_bin:
        roll_identification.initialize_roll(log)
    return log_bin

def main():
    src_file = "data/FirstWorld_Mod.txt"

    log_bin = []

    hells_rebels = classes.campaign("Hell's Rebels", dt.datetime(2022, 8, 8), ["H1 (HR)", "Zen (HR)", "D1 (HR)", "M1 (HR)"])
    hells_rebels.update_player_actor("Zen (HR)", ["Namielle", "Ercia Kash", "Zen Zombie", "Zen"])
    #hells_rebels.update_player_actor("Zen (HR)", ["Namielle", "Ercia Kash"])
    hells_rebels.update_player_actor("H1 (HR)",["Valeric", "Harnok"])
    #hells_rebels.update_player_actor("H1 (HR)",["Valeric"])
    hells_rebels.update_player_actor("D1 (HR)", ["Gage", "Rumkin", "Lieutenant_Doggo"])
    #hells_rebels.update_player_actor("D1 (HR)", ["Gage"])
    hells_rebels.update_player_actor("M1 (HR)", ["Tihana"])

    iron_gods = classes.campaign("Iron Gods", dt.datetime(2024, 1, 8), ["Harnok (IG)", "Z1 (IG)", "D1 (IG)", "M1 (IG)"])
    iron_gods.update_player_actor("Harnok (IG)", ["Construct", "Beetle Bus"])
    iron_gods.update_player_actor("Z1 (IG)", ["Sassiel GreeTrink"])
    iron_gods.update_player_actor("D1 (IG)", ["Rory"])
    iron_gods.update_player_actor("M1 (IG)", ["Verna", "Irontrunk", "Hazal/Verna/Suvi/Talvi"])
    
    ruins_azlant = classes.campaign("Ruins of Azlant", dt.datetime(2024, 9, 5), ["H1 (RA)", "Z1 (RA)", "D1 (RA)", "M1 (RA)"])
    ruins_azlant.update_player_actor("H1 (RA)", ["Garzu"])
    ruins_azlant.update_player_actor("Z1 (RA)", ["Kurina", "Kurina Owstoni"])
    ruins_azlant.update_player_actor("D1 (RA)", ["Kazell"])
    ruins_azlant.update_player_actor("M1 (RA)", ["Mavuto"])

    campaigns_bin = [hells_rebels, iron_gods, ruins_azlant]

    log_bin = pull_logs(src_file)
    #check = campaign_log_filter.log_bin_lookahead(log_bin, log_bin[4682], hells_rebels)
    if len(campaigns_bin) > 1:
        filtered_log_bin = campaign_log_filter.filter_logs(log_bin, campaigns_bin)
    #log_bin = log_handler(log_bin, campaigns_bin)

    hells_rebels.show_player_stats()
    #iron_gods.show_player_stats("Harnok (IG)")
    iron_gods.show_player_stats()

    zen = hells_rebels.fetch_player("Zen (HR)")
    this_log = zen.fetch_recent_log()
    print(this_log.actor, this_log.date_time)

    most_recent_log = hells_rebels.fetch_recent_log()

    print(most_recent_log.actor, most_recent_log.date_time)
    #zen.show_player_stats()

    #gage = hells_rebels.fetch_actor("Gage")
    #gage.show_actor_stats()

    #hells_rebels_dates = filter(return_dates, gage.logs_bin)

main()
