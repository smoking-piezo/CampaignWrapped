#! python3
# classes.py
# Class definitions for Campaign Wrapped

# TODO
# add a function to player class to tally up the stats from each actor and make player stats 
# add total rolls to actor stats 

from dataclasses import dataclass

@dataclass
class campaign():
    def __init__(self, name, player_names):
        self.name = name
        self.players_list = []

        # we're assuming that the campaign gets made first, before any players, so we'll make players as part of this
        for player_name in player_names:
            # create player object, add to player list
            new_player = player(player_name, self.name)
            self.players_list.append(new_player)
        # create that gm 
        gamemaster = player("Gamemaster", self.name)
        self.players_list.append(gamemaster)
        return
    
    def update_player_actor(self, player_name, actors_list):
        for player_obj in self.players_list: 
            if player_obj.name == player_name:
                player_to_update = player_obj
        
        for actor_name in actors_list:
            player_to_update.add_actor_from_campaign(actor_name)
        return

    def show_player_stats(self, specific_player_name=""):
        # optionally pass a specific player's name to see one player, or don't and get all players' rolls
        if specific_player_name:
            for player in self.players_list:
                if player.name == specific_player_name:
                    specific_player = player
            for actor in specific_player.actors_list: 
                if(actor.roll_count == 0):
                    break
                print(actor.name)
                counters_types = list(actor.counters)
                print("Total initialized rolls:", actor.roll_count)
                print("Total actor-related logs:", (actor.roll_count+actor.unknown_count+actor.error_count))
                print("Total un-initialized (unknown) rolls:", (actor.roll_count+actor.unknown_count+actor.error_count)-actor.roll_count)
                print("Just to be paranoid, initialized + un-initialized rolls total:", (actor.roll_count+actor.unknown_count+actor.error_count))
                for type in counters_types:
                    actor.counters[type] += log_entry.counters[type]
                for type in log_entry.acceptable_types:
                        num_of_type = len([log_entry_type for log_entry_type in actor.logs_bin if log_entry_type.entry_type == type and log_entry_type.actor == actor.name])
                        print("Number of", type, "rolls:", num_of_type)
                
        '''else:
            for player in self.players_list:
                print(player.name)
                for actor in player.actors_list:
                    if(actor.roll_count == 0):
                        break
                    counters_types = list(actor.counters)
                    for type in counters_types:
                        self.counters[type] += log_entry.counters[type]
                    print("Total initialized rolls:", actor.roll_count)
                    #print("Natural 1s rolled:", actor.counters)
                    #print("Natural 20s rolled:", actor.nat_twenty_count)
                    #print("Natural 100s rolled:", actor.nat_hundred_count)
                    print("Error rolls:", actor.error_count)
                    print("Unknown rolls:", actor.unknown_count)
        '''
        return

    def list_player_actors(self):
        campaign_actors = []
        # we care only about the actors that aren't the gamemaster 
        for player in self.players_list:
            if player.name == "Gamemaster":
                break
            for actor in player.actors_list:
                campaign_actors.append(actor.name)
        return campaign_actors 
    
    def fetch_actor(self, actor_name):
        for player in self.players_list:
            for actor in player.actors_list:
                if actor.name == actor_name:
                    return actor 

class player():
    def __init__(self, name, campaign):
        # start the player object with the name of the player and name of its campaign
        self.name = name
        
        # how do we manage making sure a player is added to multiple campaigns? what if the desired campaign object hasn't been made yet? 
        # just say NO to multiple campaigns and make a new player object for each campaign 
        self.campaign = campaign
        
        # we'll add actors later as a function 
        self.actors_list = []
        return
        
    def add_actor_from_campaign(self, actor_name):
        actor_exists = isinstance(actor_name, actor)
        if actor_exists:
            if actor_name not in self.actors_list:
                self.actors_list.append(actor_name)
        else: 
            new_actor = actor(actor_name, self.name)
            self.actors_list.append(new_actor)
        return  
            
class actor():
    error_count = 0 
    unknown_count = 0 
    counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}
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
        return 

    def __init__(self, name, player, logs_bin=[]):
        self.name = name
        self.player = player 
        self.logs_bin = logs_bin
        logs_count = len(logs_bin)
        if logs_count > 0:
            for i in range(0,logs_count): 
                roll_count += logs_bin[i].roll_count
        else:
            roll_count = 0
        self.roll_count = roll_count
        return

class log_entry():
    acceptable_types = ["Unknown", "Initiative", "Level Up", "Will Saving Throw", "Reflex Saving Throw", 
                        "Fortitude Saving Throw", 'Unknown Saving Throw', "Skill Check", "Attack",
                        "Spell Cast", "Item / Potion Used", "Raw Roll", "Chat Message", "Ability Test",
                        "Combat Maneuver Bonus", "Caster Level Check", "Defenses", "Concentration Check", "Error"]
    error_flag = False 
    unknown_flag = True 
    counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}

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
    
    def update_type(self, roll_type):
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
        return self.entry_type

    def __init__(self, date_time, actor, log_lines, entry_type):
        self.date_time = date_time
        self.actor = actor
        self.log_lines = log_lines 
        self.roll_bin = []
        self.roll_count = 0
        self.entry_type = "Unknown"
        self.entry_type = self.update_type(entry_type)
        return

class die_roll():
    counters = {'Natural 1 Count': 0, 'Natural 20 Count': 0, 'Natural 100 Count': 0}

    def __init__(self, dx_type, dx_result, result_w_mods):
        self.dx_type = dx_type
        self.dx_result = dx_result
        if result_w_mods:
            self.result_w_mods = result_w_mods
        else: 
            self.result_w_mods = dx_result

        self.counters = self.notable_rolls(dx_type, dx_result)
        return
    
    def notable_rolls(self, dx_type, dx_result):
        if dx_result == 1:
            self.counters['Natural 1 Count'] += 1
        
        if dx_result == 20 and dx_type == "d20":
            self.counters['Natural 20 Count'] += 1

        if dx_result == 100 and dx_type == "d100":
            self.counters['Natural 100 Count'] += 1
        return self.counters