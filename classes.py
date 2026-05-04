#! python3
# classes.py
# Class definitions for Campaign Wrapped

# TODO
# add a function to player class to tally up the stats from each actor and make player stats 
# add total rolls to actor stats 

from dataclasses import dataclass
import datetime

@dataclass
class campaign():
    def __init__(self, name, start_date, player_names):
        self.name = name
        self.players_list = []

        # we're assuming that the campaign gets made first, before any players, so we'll make players as part of this
        for player_name in player_names:
            # create player object, add to player list
            new_player = player(player_name, self.name)
            self.players_list.append(new_player)
        # create that gm 
        self.gamemaster_name = "Gamemaster " + self.name
        gamemaster = player(self.gamemaster_name, self.name)
        self.players_list.append(gamemaster)
        self.start_date = start_date
        self.latest_log = None
        return
    
    def force_latest_log_update(self):
        self.latest_log = self.fetch_recent_log()
        return
    
    def update_player_actor(self, player_name, actors_list):
        for player_obj in self.players_list: 
            if player_obj.name == player_name:
                player_to_update = player_obj
        
        for actor_name in actors_list:
            player_to_update.add_actor_from_campaign(actor_name)

        self.latest_log = self.fetch_recent_log()
        return

    def show_player_stats(self, specific_player_name=""):
        # optionally pass a specific player's name to see one player, or don't and get all players' rolls
        if specific_player_name:
            for player in self.players_list:
                if player.name == specific_player_name:
                    player.show_player_stats()                
        else:
            for player in self.players_list:
                player.show_player_stats()    
        return
    
    def list_actor_objs(self):
        actor_objs = []
        for player in self.players_list:
            player_actors = []
            player_actors = (player.list_actors_objs())
            for actor in player_actors:
                actor_objs.append(actor)
        return actor_objs
    
    def list_npc_actors(self):
        npc_actors = []
        gamemaster = self.fetch_player(self.gamemaster_name)
        npc_actors = gamemaster.list_actors()
        return npc_actors

    def list_player_actors(self):
        campaign_actors = []
        # we care only about the actors that aren't the gamemaster 
        for player in self.players_list:
            if player.name == self.gamemaster_name:
                break
            for actor in player.actors_list:
                campaign_actors.append(actor.name)
        return campaign_actors 
    
    def fetch_actor(self, actor_name):
        for player in self.players_list:
            for actor in player.actors_list:
                if actor.name == actor_name:
                    return actor 
                
    def fetch_player(self, player_name):
        for player in self.players_list:
            if player.name == player_name:
                return player
            else:
                return None
    
    def fetch_recent_log(self):
        recent_log = []
        for each in self.players_list:
            if each.fetch_recent_log() is not None:
                recent_log.append(each.fetch_recent_log())
                if self.latest_log is None:
                    self.latest_log = each.fetch_recent_log()
        
        if all(items is None for items in recent_log) and self.latest_log is None:
            # if each actor has no recent log then we've just initialized
            return self.latest_log
            
        for log in recent_log:
            if (self.latest_log.date_time - log.date_time) < datetime.timedelta(0):
                # if negative, then log_datetime is more recent
                self.latest_log = log
        return self.latest_log


class player():
    def __init__(self, name, campaign):
        # start the player object with the name of the player and name of its campaign
        self.name = name
        
        # how do we manage making sure a player is added to multiple campaigns? what if the desired campaign object hasn't been made yet? 
        # just say NO to multiple campaigns and make a new player object for each campaign 
        self.campaign = campaign
        
        # we'll add actors later as a function 
        self.actors_list = []
        self.latest_log = None
        self.latest_log = self.fetch_recent_log()
        return
    
    def fetch_recent_log(self):
        recent_log = []
        for item in range(0, len(self.actors_list)):
            recent_log.append(self.actors_list[item].latest_log)
            if recent_log[item] is not None and self.latest_log is None:
                self.latest_log = recent_log[item]
        
        recent_log = [log for log in recent_log if log is not None]
            
        if all(items is None for items in recent_log) and self.latest_log is None:
            # if each actor has no recent log then we've just initialized
            return self.latest_log

        for log in recent_log:
            if (self.latest_log.date_time - log.date_time) < datetime.timedelta(0):
                # if negative, then log_datetime is more recent
                self.latest_log = log
        
        return self.latest_log        

    def list_actors(self):
        player_actors = []
        for each in self.actors_list:
            player_actors.append(each.name)
        
        return player_actors
    
    def list_actors_objs(self):
        player_actors_objs = []
        for each in self.actors_list:
            player_actors_objs.append(each)
        return player_actors_objs
        
    def add_actor_from_campaign(self, actor_name):
        actor_exists = isinstance(actor_name, actor)
        if actor_exists:
            if actor_name not in self.actors_list:
                self.actors_list.append(actor_name)
        else: 
            new_actor = actor(actor_name, self.name)
            self.actors_list.append(new_actor)
        
        return  
    
    def show_player_stats(self):
        counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}
        total_roll_count = 0
        counters_types = list(counters.keys())
        roll_types = tuple(log_entry.acceptable_types)
        roll_types_count = {}
        num_actors = len(self.actors_list)
        for key in roll_types:
                roll_types_count[key] = 0
        if num_actors > 1: 
            # if there's more than one actor, let's sum up all the counts
            if num_actors > 5:
                print(self.name, "has more than 5 actors.")
            else:
                print(self.name, "has the following actors:")           
            for each in self.actors_list:
                if num_actors < 5: 
                    print(each.name)
                total_roll_count += each.roll_count
                for type in counters_types:
                    counters[type] += len([log_with_counter for log_with_counter in each.logs_bin if log_with_counter.counters[type] > 0])
                for type in roll_types:
                    num_of_type = len([log_entry_type for log_entry_type in each.logs_bin if log_entry_type.entry_type == type and log_entry_type.actor == each.name])
                    roll_types_count[type] += num_of_type
            for counter_type, counter_value in counters.items():
                print(f"{counter_type}: {counter_value}")
            for type, value in roll_types_count.items():
                print(f"{type}: {value}")  
            print(self.name, "has", len(self.actors_list), "actors who rolled a total of", total_roll_count, "times.")
        elif len(self.actors_list) == 1:
            # if there's only one actor, show that actor's stats
            self.actors_list[0].show_actor_stats()
            print(self.name, "has 1 actor who rolled a total of", self.actors_list[0].roll_count, "times.")
        elif len(self.actors_list) == 0:
            print(self.name, "has no actor objects.")
            
class actor():
    def __init__(self, name, player):
        self.name = name
        self.player = player 
        self.logs_bin = []
        self.logs_count = 0
        self.roll_count = 0
        self.counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}
        self.error_count = 0 
        self.unknown_count = 0 
        self.latest_log = None
        return

    def add_log(self, log_entry):
        self.logs_bin.append(log_entry)
        self.logs_count = len(self.logs_bin)
        self.roll_count = self.roll_count + log_entry.roll_count
        counters_types = list(self.counters)
        for type in counters_types:
            self.counters[type] += log_entry.counters[type]
            #print(self.name, type, self.counters[type])
        if log_entry.error_flag:
            self.error_count += 1
        if log_entry.unknown_flag: 
            self.unknown_count += 1
        self.latest_log = self.update_recent_log(log_entry)
        return 

    def update_recent_log(self, log_entry):
        # if latest_log is None, then log_entry is the first and therefore most recent
        if self.latest_log is None:
            return log_entry
        # if log_entry datetime minus latest_log datetime is negative, then latest_log is more recent
        if (log_entry.date_time - self.latest_log.date_time) < datetime.timedelta(0):
            return self.latest_log
        else:
            return log_entry
    
    def show_actor_stats(self):
        counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}
        print(self.name)
        counters_types = list(counters)
        print("Total actor-related logs:", (self.logs_count))
        print("Total roll count in logs:", self.roll_count)
        print("Total unknown type logs:", (self.unknown_count + self.error_count))
        # need to fix this
        #for type in counters_types:
            #self.counters[type] += log_entry.counters[type]
        for type in log_entry.acceptable_types:
            num_of_type = len([log_entry_type for log_entry_type in self.logs_bin if log_entry_type.entry_type == type and log_entry_type.actor == self.name])
            print("Number of", type, "rolls:", num_of_type)
        for skill_type in log_entry.skill_types: 
            num_of_skilltype = len([log_entry_skilltype for log_entry_skilltype in self.logs_bin if log_entry_skilltype.skill_type == skill_type and log_entry_skilltype.actor == self.name])
            print("Number of", skill_type, "rolls:", num_of_skilltype)
        return

class log_entry():
    acceptable_types = ["Unknown", "Initiative", "Level Up", "Will Saving Throw", "Reflex Saving Throw", 
                        "Fortitude Saving Throw", 'Unknown Saving Throw', "Skill Check", "Attack",
                        "Spell Cast", "Item Used", "Raw Roll", "Chat Message", "Ability Test",
                        "Combat Maneuver Bonus", "Caster Level Check", "Defenses", "Concentration Check", "Error"]
    skill_types = ["Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device", "Disguise",
                   "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Knowledge", "Linguistics", 
                   "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand", "Spellcraft",
                   "Stealth", "Survival", "Swim", "Use Magic Device"]
    deep_skills = ["Craft", "Knowledge", "Perform", "Profession"]
    knowledges = ["Arcana", "Dungeoneering", "Engineering", "Geography","History", "Local", "Nature", "Nobility", "Planes", "Religion"]
    # TODO: pull the types of Craft, Perform, Profession from the roll line 

    def __init__(self, date_time, actor, log_lines, entry_type):
        self.date_time = date_time
        self.actor = actor
        self.log_lines = log_lines 
        self.roll_bin = []
        self.roll_count = 0
        self.entry_type = "Unknown"
        self.error_flag = False 
        self.unknown_flag = True 
        self.counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}
        self.entry_type, self.skill_type = self.update_type(entry_type, log_lines)
        return

    def add_roll(self, roll_object):
        if len(self.roll_bin) >= 0:
            self.roll_bin.append(roll_object)
        else:
            self.roll_bin = [roll_object]
        self.roll_count = len(self.roll_bin)
        counter_types = list(self.counters.keys())
        for type in counter_types:
            self.counters[type] += roll_object.counters[type]
        return 
    
    def update_type(self, roll_type, log_lines):
        if self.entry_type == "Error":
            self.error_flag = True
        if self.entry_type == "Unknown":
            self.unknown_flag = True
        if roll_type in self.acceptable_types:
            self.entry_type = roll_type
            self.unknown_flag = False
            self.error_flag = False
        elif roll_type:
            self.entry_type = "Error"
            self.error_flag = True
            print(self.date_time)
        else: 
            self.entry_type = "Unknown"
            self.unknown_flag = True
            
        roll_id_split = log_lines[2].split(" ")

        if roll_type == "Skill Check":
            # set the skill type! otherwise skill type = N/A
            roll_id_split.remove("Skill")
            roll_id_split.remove("Check")

            if len(roll_id_split) > 1:
                self.skill_type = " ".join(roll_id_split)
            else:
                self.skill_type = roll_id_split[0]

        else:
            self.skill_type = "N/A"
        return self.entry_type, self.skill_type

class die_roll():

    def __init__(self, dx_type, dx_result, result_w_mods):
        self.counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}
        self.dx_type = dx_type
        self.dx_result = dx_result
        if result_w_mods:
            self.result_w_mods = result_w_mods
        else: 
            self.result_w_mods = dx_result
        self.notable_rolls(dx_type, dx_result)
        
        return
    
    def notable_rolls(self, dx_type, dx_result):
        if dx_result == 1:
            self.counters['Natural 1 Count'] += 1
        
        if dx_result == 20 and dx_type == "d20":
            self.counters['Natural 20 Count'] += 1

        if dx_result == 100 and dx_type == "d100":
            self.counters['Natural 100 Count'] += 1
        return self.counters
