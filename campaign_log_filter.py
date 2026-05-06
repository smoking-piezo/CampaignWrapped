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
        log_campaign = None

        # first, if the log.date_time is before the campaign.start_date then it can't be in that campaign
        for each in campaigns_bin:
            if (each.start_date - log.date_time) <= dt.timedelta(0):
                # if true, then log.date_time is AFTER the campaign start time
                possible_campaigns.append(each)
            
            # let's check each campaign's latest log. If we're not at the first roll of the day, then we can check the latest log against the current log's date. same day means we've matched the campaign
            # note that initialization and first log of the day are important edge cases, since the latest log function won't be terribly useful, since there won't be any logs for us to compare to yet/none for the day! 
            # considering that it's POSSIBLE for an npc actor to have the same name but actually be two separate creatures in separate campaigns, let's check the log date first. 
            # if there IS a latest_log, then let's compare the dates. 

                if each.latest_log is not None: 
                    # if there is a latest_log for the campaign, let's see if our log is the same day or the first log of the day 
                    log_campaign_diff = log.date_time - each.latest_log.date_time
                    if log_campaign_diff <= same_day:
                        # if it's the same day, we've found a sure match!
                        # hey... turns out that's not true 
                        log_campaign = each
                        possible_campaigns = []
                        break
            
            # we get here if: 1) there isn't a latest log for the campaign, 2) the latest log is more than a day away (which could indicate the wrong campaign OR that this is the first log of the day)
            # regardless, let's check using the lookahead function. we'll see if the each campaign in the current for loop is a match for the current day by looking ahead in the log to find a PC to match a campaign

            same_campaign_check = log_bin_lookahead(log_bin, log, each)
            if same_campaign_check:
                # this is a sure match! 
                log_campaign = each
                possible_campaigns = []
                break
        
        # debugging code, delete me later, just trying to flag if we failed to find a sure match
        if log_campaign is None and len(possible_campaigns) == 1:
            log_campaign = possible_campaigns[0]
        elif log_campaign is None and len(possible_campaigns) > 1:
            raise ValueError("Did not find campaign")
        
        # great, we found the campaign, that's the hard part. now to find the actor and apply the log
        possible_actors = log_campaign.list_actor_objs()
        matching_actors = []

        for actor in possible_actors:
            if actor.name == log.actor: 
                matching_actors.append(actor)

        if len(matching_actors) == 0:
            # no matches, so it's a new npc to be assigned to the GM
            gamemaster_name = log_campaign.gamemaster_name
            log_campaign.update_player_actor(gamemaster_name, [log.actor])
            actor_obj = log_campaign.fetch_actor(log.actor)

        elif len(matching_actors) == 1:
            # if there is a match, we need to discern whether it's the right match, or if there's a new NPC that belongs to a different campaign with the same name
            # or if it's a PC, in which case we know which campaign it's from 
            if matching_actors[0].player.startswith("Gamemaster"):
                # Do we need to doublecheck this?? 
                # let's just go with it for now
                actor_obj = matching_actors[0]
            else:
                actor_obj = matching_actors[0]
        elif len(matching_actors) > 1:
            print("PANIC!!! MORE THAN ONE MATCHING ACTOR", log.actor, matching_actors)

        if actor_obj is not None:
            actor_obj.add_log(log)
            log_campaign.force_latest_log_update()
        else:
            raise ValueError([actor_obj, log.log_lines, "Actor object not found for current log"])

    return filtered_log_bin

def log_bin_lookahead(log_bin, log, campaign):
    log_index = 0
    log_date = log.date_time
    same_day = dt.timedelta(days = 1)
    campaign_player_actors = campaign.list_player_actors()
    campaign_match = False
    
    for index in range(0, len(log_bin)): 
        if log_bin[index] == log:
            log_index = index
            break
        
    index_date = log_bin[log_index].date_time
    date_check = index_date - log_date
    checking_index = log_index + 1
    loop_count = 0

    # okay, this while loop is slow and limited 
    # can we just pull all logs where the log_date is within abs(dt.timedelta(day = 1))

    same_day_log_bin = [same_day_log for same_day_log in log_bin if abs(index_date - same_day_log.date_time) <= same_day]
    same_day_actors = []
    
    for each in same_day_log_bin:
        same_day_actors.append(each.actor)
    
    # turn the lists into sets and compare - any intersections means a campaign match
    campaign_player_actors = set(campaign_player_actors)
    same_day_actors = set(same_day_actors)
    same_day_player_actors = campaign_player_actors.intersection(same_day_actors)

    if(same_day_player_actors):
        campaign_match = True
        return campaign_match

    '''
    while True:
        if dt.timedelta(0) <= date_check <= same_day:
            if log_bin[checking_index].actor in campaign_player_actors:
                campaign_match = True
                return campaign_match
            if checking_index < len(log_bin)-1:
                checking_index += 1 
                checking_date = log_bin[checking_index].date_time
                loop_count += 1
                date_check = checking_date - log_date
                if loop_count < 10 and date_check > same_day:
                    # if we checked fewer than 10 logs, then we were at the end of the day and didn't get a good sample 
                    # so let's retry the loop at 10 logs before the log_index? 
                    checking_index = log_index - 10
                    checking_date = log_bin[checking_index].date_time
                    date_check = checking_date - log_date
                    # what's screwing this logic over is a day that the GM rolled two whole rolls on NPCs. 
                if loop_count > 30:
                    break
        else:
            break
    '''
    return campaign_match
