#! python3
# pathfinder1e_campaignwrapped.py - Pathfinder 1e Campaign Wrapped 
# A silly program meant to pull combat stats from a Pathfinder 1e chat log so players can reminisce over their good and bad rolls.  

# TODO 
# how are we gonna handle tallying up the types of skill checks by skill types? 
# differentiate campaigns by date/character?
# correct the campaign class's show player stats function to utilize the player class's function instead 
# for the log handler function, it doesn't really matter if they're NPCs or PCs. we know which ones are PCs. so let's flatten that logic into one list

# remove roll from data file dated [1/8/2024, 8:09:05 PM] Boris

import datetime as dt
import os
import roll_identification, classes, campaign_log_filter



def match_campaign_new_actor(campaigns_bin, log):
    # the current log actor is NOT in the PC actors list or NPC actors list for any current campaign
    # this means they are an NPC from an unknown campaign and we need to do some date matching to figure it out
    # first, if the log.date_time is earlier than a campaign's start date, then it can't be part of that campaign 
    possible_campaign = []
    for each in campaigns_bin:
        if log.date_time > each.start_date:
            possible_campaign.append(each)
    # if there's only one entry in the possible_campaign list, huzzah, there's only one option! 
    if len(possible_campaign) == 1: 
        # here we're assuming we know that we have an NPC and know which campaign it belongs to
        # so let's create an actor for it, assign it to the campaign's GM
        # we are NOT assigning the log to the actor here, that is done in the LOG HANDLER 
        log_campaign = possible_campaign[0]
        gamemaster_name = log_campaign.gamemaster_name
        log_campaign.update_player_actor(gamemaster_name, [log.actor])
        actor_obj = log_campaign.fetch_actor(log.actor)
    elif len(possible_campaign) < 1:
        # This shouldn't happen. 
        raise ValueError ("This log's datetime is before any campaign's start date")
    elif len(possible_campaign) > 1: 
        # so we have a log that is after the start date of multiple campaigns and now we have to do some serious date matching
        # CHANGE THIS VALUE OF ACTOR_OBJ
        actor_obj = None
        pass
    return actor_obj

def match_campaign_existing_actor(campaigns_bin, log, matching_actors):
    # this function needs to return log_campaign, and the matching actor_obj
    # we THINK that the log belongs to one of the existing actors in the list matching_actors
    # it's POSSIBLE there's another NPC actor with the same name across multiple campaigns though
    # but tbh, if there's only one object in matching_actors and it's a player object, I think we can guess that it's a player 

    # CHANGE THIS 
    actor_obj = None
    log_campaign = []

    if len(matching_actors) == 1 and not matching_actors[0].player.startswith("Gamemaster"):
        #PCs only
        actor_obj = matching_actors[0]
        for campaign in campaigns_bin:
            if campaign.fetch_player(actor_obj.player):
                log_campaign.append(campaign)

    if len(matching_actors) == 1 and not log_campaign:
        #NPCs only. so we double-check that we really do have the right campaign, then move on
        actor_obj = matching_actors[0]
        for campaign in campaigns_bin:
            if campaign.fetch_player(actor_obj.player):
                log_campaign.append(campaign)
                if (log_campaign[-1].start_date - log.date_time) > dt.timedelta(0):
                    # if the timedelta is positive, then the log datetime is BEFORE the campaign's start date, meaning it's NOT the right campaign
                    log_campaign.remove(campaign)

        # if the timedelta between log.date_time and log_campaign.latest_log is less than a day, then we know for sure that we have a match!
        match_time = dt.timedelta(days=1)
        log_campaign_diff = log.date_time - log_campaign[0].latest_log.date_time 
        if log_campaign_diff > match_time:
            raise ValueError("The timedelta between the campaign's last log and the current log is greater than one day, do we have the right campaign?")

    # one final check before we return value: we should have removed all other possibilities from log_campaign to only one 
    if len(log_campaign) > 1:
        raise ValueError(log.lines, log_campaign, "There should only be one actor")

    return actor_obj

def log_handler(log_bin, campaigns_bin): 
    for log in log_bin:
        all_actors = updated_actors_lists(campaigns_bin)

        

    return log_bin

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

def return_dates(log_entry):
    return log_entry.date_time

def main():
    src_file = "data/FirstWorld_Mod.txt"

    log_bin = []

    hells_rebels = classes.campaign("Hell's Rebels", dt.datetime(2022, 8, 8), ["H1 (HR)", "Zen (HR)", "D1 (HR)", "M1 (HR)"])
    hells_rebels.update_player_actor("Zen (HR)", ["Namielle", "Ercia Kash"])
    hells_rebels.update_player_actor("H1 (HR)",["Valeric"])
    hells_rebels.update_player_actor("D1 (HR)", ["Gage"])
    hells_rebels.update_player_actor("M1 (HR)", ["Tihana"])

    iron_gods = classes.campaign("Iron Gods", dt.datetime(2024, 1, 8), ["Harnok (IG)", "Z1 (IG)", "D1 (IG)", "M1 (IG)"])
    iron_gods.update_player_actor("Harnok (IG)", ["Construct", "Harnok"])
    iron_gods.update_player_actor("Z1 (IG)", ["Sassiel GreeTrink"])
    iron_gods.update_player_actor("D1 (IG)", ["Rory"])
    iron_gods.update_player_actor("M1 (IG)", ["Verna", "Irontrunk", "Hazal/Verna/Suvi/Talvi"])
    
    ruins_azlant = classes.campaign("Ruins of Azlant", dt.datetime(2024, 9, 5), ["H1 (RA)", "Z1 (RA)", "D1 (RA)", "M1 (RA)"])
    ruins_azlant.update_player_actor("H1 (RA)", ["Garzu"])
    ruins_azlant.update_player_actor("Z1 (RA)", ["Kurina"])
    ruins_azlant.update_player_actor("D1 (RA)", ["Kazell"])
    ruins_azlant.update_player_actor("M1 (RA)", ["Mavuto"])

    campaigns_bin = [hells_rebels, iron_gods, ruins_azlant]

    log_bin = pull_logs(src_file)
    if len(campaigns_bin) > 1:
        filtered_log_bin = campaign_log_filter.filter_logs(log_bin, campaigns_bin)
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
