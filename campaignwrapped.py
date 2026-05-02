#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

# TODO 
# how are we gonna handle tallying up the types of skill checks by skill types? 
# differentiate campaigns by date/character?
# correct the campaign class's show player stats function to utilize the player class's function instead 

from datetime import datetime
import os
import roll_identification, classes

def updated_actors_lists(campaigns_bin):
    player_actors = []
    npc_actors = []
    for campaign in campaigns_bin:
        # get all player actors
        campaign_player_actors = []
        campaign_player_actors = campaign.list_player_actors()
        player_actors.extend(campaign_player_actors)

        # get all npc actors
        npcs = campaign.list_npc_actors()
        npc_actors.extend(npcs)
    
    return player_actors, npc_actors


def log_handler(log_bin, campaigns_bin): 
    for log in log_bin:
        log.date_time = roll_identification.find_roll_date(log.log_lines)
        log.actor = roll_identification.find_actor(log.log_lines)
        roll_identification.initialize_roll(log)
        
        # if this log's actor is not in the player_actors list, then it's an NPC 
        player_actors, npc_actors = updated_actors_lists(campaigns_bin)
        if log.actor not in player_actors and log.actor not in npc_actors:
            # then we figure out which campaign it belongs to, and assign it to that campaign's GM
            # first, if the log.date_time is earlier than a campaign's start date, then it can't be part of that campaign 
            possible_campaign = []
            for each in campaigns_bin:
                if log.date_time > each.start_date:
                    possible_campaign.append(each)
            # if there's only one entry in the possible_campaign list, huzzah, there's only one option! 
            if len(possible_campaign) == 1: 
                # here we're assuming we know that we have an NPC and know which campaign it belongs to
                # so let's create an actor for it and assign it to the campaign's GM 
                # we had to make separate GM names for each campaign so the program didn't overlap the different bins so let's find the right GM 
                picked_campaign = possible_campaign[0]
                gamemaster_name = picked_campaign.gamemaster_name
                picked_campaign.update_player_actor(gamemaster_name, [log.actor])
                npc_actor = picked_campaign.fetch_actor(log.actor)
                npc_actor.add_log(log)
                continue
            elif len(possible_campaign) < 1:
                raise ValueError ("This log's datetime is before any campaign's start date")
            elif len(possible_campaign) > 1: 
                # so we have a log that is after the start date of multiple campaigns
                pass


        for this_campaign in campaigns_bin:
            # if the actor's name is in the campaign's PC list and the log's date is after the start date of the campaign
            # but honestly we should do some better date handling probably 
            if log.actor in this_campaign.list_player_actors() and log.date_time > this_campaign.start_date: 
                actor_obj = this_campaign.fetch_actor(log.actor)
                actor_obj.add_log(log)
                break
            if log.actor in this_campaign.list_npc_actors() and log.date_time > this_campaign.start_date:
                actor_obj = this_campaign.fetch_actor(log.actor)
                actor_obj.add_log(log)
            else:
                 pass
            # this is where we figure out if this log belongs to a different campaign or the gm 
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

    hells_rebels = classes.campaign("Hell's Rebels", datetime(2022, 8, 8), ["H1", "Zen (HR)", "D1", "M1"])
    hells_rebels.update_player_actor("Zen (HR)", ["Namielle", "Ercia Kash"])
    hells_rebels.update_player_actor("H1",["Valeric"])
    hells_rebels.update_player_actor("D1", ["Gage"])
    hells_rebels.update_player_actor("M1", ["Tihana"])

    iron_gods = classes.campaign("Iron Gods", datetime(2024, 1, 8), ["Harnok (IG)", "Z1", "D1", "M1"])
    iron_gods.update_player_actor("Harnok (IG)", ["Construct", "Harnok"])
    iron_gods.update_player_actor("Z1", ["Sassiel GreeTrink"])
    iron_gods.update_player_actor("D1", ["Rory"])
    iron_gods.update_player_actor("M1", ["Verna", "Irontrunk", "Hazal/Verna/Suvi/Talvi"])
    
    ruins_azlant = classes.campaign("Ruins of Azlant", datetime(2024, 9, 5), ["H1", "Z1", "D1", "M1"])
    ruins_azlant.update_player_actor("H1", ["Garzu"])
    ruins_azlant.update_player_actor("Z1", ["Kurina"])
    ruins_azlant.update_player_actor("D1", ["Kazell"])
    ruins_azlant.update_player_actor("M1", ["Mavuto"])

    campaigns_bin = [hells_rebels, iron_gods, ruins_azlant]

    log_bin = pull_log_lines(src_file)
    log_bin = log_handler(log_bin, campaigns_bin)

    hells_rebels.show_player_stats()
    #iron_gods.show_player_stats("Harnok (IG)")
    #iron_gods.show_player_stats()

    zen = hells_rebels.fetch_player("Zen (HR)")
    log = zen.fetch_recent_log()
    print(log.actor, log.date_time)

    most_recent_log = hells_rebels.fetch_recent_log()
    print(most_recent_log.actor, most_recent_log.date_time)
    #zen.show_player_stats()

    #gage = hells_rebels.fetch_actor("Gage")
    #gage.show_actor_stats()

    #hells_rebels_dates = filter(return_dates, gage.logs_bin)

main()