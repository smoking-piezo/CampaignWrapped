#! python3
# campaign_log_filter.py 
# This script is intended to filter a log with multiple campaigns into separate logs 

import datetime as dt
import classes

def filter_logs(log_bin, campaigns_bin):
    # log_bin is a list that contains all the log_entry objects in the source file log
    # campaigns_bin is a list that contains all campaign objects associated with the source file log
    # filter_logs should return a dictionary, with the keys being the campaign names and the values being a list of the associated log_entries for that campaign 
    campaign_names = []
    for campaign in campaigns_bin:
        campaign_names.append(campaign.name)
    filtered_log_bin = dict.fromkeys(campaign_names, [])

    # now we filter through log_bin and separate out all the logs. 
    # two major factors need to match: actors and dates 
    # let's filter by date first? 
    # we can't until we filter by actor first because a log has to be initialized to an actor for a campaign to have a latest_log entry

    for log in log_bin:
        possible_campaigns = []
        same_day = dt.timedelta(days = 1)

        # first, if the log.date_time is before the campaign.start_date then it can't be in that campaign
        for each in campaigns_bin:
            if (each.start_date - log.date_time) < dt.timedelta(0):
                # if true, then log.date_time is AFTER the campaign start time
                possible_campaigns.append(each)
            
            # two ways to go from here: we can check if there's a matching actor in the possible_campaigns OR we can check if the log's date matches a campaign's latest log 
            # note that initialization is an important edge case, since the latest log function won't be terribly useful, since there won't be any logs for us to compare to yet! 
            # considering that it's POSSIBLE for an npc actor to have the same name but actually be two separate creatures in separate campaigns, let's check the log date first. 
            # if there IS a latest_log, then let's compare the dates. 

                if each.latest_log is not None: 
                    # if there is a latest_log for the campaign, let's see if our log is the same day or the first log of the day 
                    log_campaign_diff = log.date_time - each.latest_log.date_time
                    if log_campaign_diff > same_day:
                        # ok, it's not the same day, but, is it the first roll of the day for this campaign?
                        same_campaign_check = new_day_same_campaign(log_bin, log, each)
                        if same_campaign_check:
                            possible_campaigns = [each]
                            break

        possible_actors = updated_actors_lists(possible_campaigns)
        matching_actors = []

        for each in possible_actors:
            if each.name == log.actor: 
                matching_actors.append(each)

        if len(matching_actors) == 0:
            # no matches, so it's a new npc. 
            if len(possible_campaigns) == 1:
                log_campaign = possible_campaigns[0]
                gamemaster_name = log_campaign.gamemaster_name
                log_campaign.update_player_actor(gamemaster_name, [log.actor])
                actor_obj = log_campaign.fetch_actor(log.actor)
            else:
                # we need to do some more filtering
                raise ValueError("There's more than one possible campaign for this new NPC.")
        elif len(matching_actors) == 1:
            # if there is a match, we need to discern whether it's the right match, or if there's a new NPC that belongs to a different campaign with the same name
            # or if it's a PC, in which case we know which campaign it's from 
            if matching_actors[0].player.startswith("Gamemaster"):
                # then we need do to something else 
                print(log.log_lines)
                player = matching_actors[0].player
                for this in possible_campaigns:
                    check_player = this.fetch_player(player)
                    if check_player is not None:
                        log_campaign = campaign
            else:
                actor_obj = matching_actors[0]
                player = actor_obj.player
                for this in possible_campaigns:
                    check_player = this.fetch_player(player)
                    if check_player is not None:
                        log_campaign = this

        if actor_obj is not None:
            actor_obj.add_log(log)
            log_campaign.force_latest_log_update()
        else:
            raise ValueError([actor_obj, log.log_lines, "Actor object not found for current log"])
        
        



    return filtered_log_bin

def new_day_same_campaign(log_bin, log, campaign):
    log_index = 0
    log_date = log.date_time
    same_day = dt.timedelta(days = 1)
    campaign_player_actors = campaign.list_player_actors()
    campaign_match = False
    
    for index in range(0, len(log_bin)): 
        if log_bin[index] == log:
            log_index = index
        
    index_date = log_bin[log_index].date_time
    while (index_date - log_date) <= same_day:
        if log_bin[log_index].actor in campaign_player_actors:
            campaign_match = True
            return campaign_match
        if log_index < len(log_bin):
            log_index += 1 
            index_date = log_bin[log_index].date_time
        else:
            break
    
    return campaign_match
    
            


    

def updated_actors_lists(campaigns_bin):
    all_actors = []
    try:
        for campaign in campaigns_bin:
            # get all player actors
            campaign_player_actors = []
            campaign_player_actors = campaign.list_actor_objs()
            all_actors.extend(campaign_player_actors)
    except:
        all_actors = campaigns_bin.list_actor_objs()

    return all_actors
