#! python3
# classes.py
# Class definitions for Campaign Wrapped

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

    def show_player_stats(self):
        for player in self.players_list:
            print(player.name)
            for actor in player.actors_list:
                if(actor.roll_count == 0):
                    break
                print(actor.name)
                print("Total rolls:", actor.roll_count)
                print("Natural 1s rolled:", actor.nat_one_count)
                print("Natural 20s rolled:", actor.nat_twenty_count)
                print("Natural 100s rolled:", actor.nat_hundred_count)
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
    def add_log(self, log_entry):
        if self.logs_bin:
            self.logs_bin.append(log_entry)
        else:
            self.logs_bin = [log_entry]
        self.logs_count = len(self.logs_bin)
        self.roll_count = self.roll_count + log_entry.roll_count

        if log_entry.nat_one_count: 
            self.nat_one_count += log_entry.nat_one_count
        if log_entry.nat_twenty_count:
            self.nat_twenty_count += log_entry.nat_twenty_count
        if log_entry.nat_hundred_count:
            self.nat_hundred_count += log_entry.nat_hundred_count
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
        self.nat_one_count = 0
        self.nat_twenty_count = 0
        self.nat_hundred_count = 0
        return

class log_entry():
    acceptable_types = ["Unknown", "Initiative", "Level Up", "Will Saving Throw", "Reflex Saving Throw", 
                        "Fortitude Saving Throw", 'Unknown Saving Throw', "Skill Check", "Attack",
                        "Spell Cast", "Item / Potion Used", "Raw Roll", "Chat Message", "Ability Test",
                        "Combat Maneuver Bonus", "Caster Level Check", "Defenses", "Concentration Check", "Error"]
    
    def add_roll(self, roll_object):
        if len(self.roll_bin) >= 0:
            self.roll_bin.append(roll_object)
        else:
            self.roll_bin = [roll_object]
        self.roll_count = len(self.roll_bin)

        if roll_object.nat_one_flag:
            self.nat_one_count += 1
        if roll_object.nat_twenty_flag:
            self.nat_twenty_count += 1
        if roll_object.nat_hundred_flag:
            self.nat_hundred_count += 1
        return 
    
    def update_type(self, roll_type):
        if roll_type in self.acceptable_types:
            self.entry_type = roll_type
        elif roll_type:
            self.entry_type = "Error"
        else: 
            self.entry_type = "Unknown"
        return self.entry_type

    def __init__(self, date_time, actor, log_lines, entry_type):
        self.date_time = date_time
        self.actor = actor
        self.log_lines = log_lines 
        self.roll_bin = []
        self.roll_count = 0
        self.nat_one_count = 0
        self.nat_twenty_count = 0
        self.nat_hundred_count = 0
        if entry_type in self.acceptable_types:
            self.entry_type = entry_type
        elif entry_type:
            self.entry_type = "Error"
        else: 
            self.entry_type = "Unknown"
        return

class die_roll():
    def __init__(self, dx_type, dx_result, result_w_mods):
        self.dx_type = dx_type
        self.dx_result = dx_result
        if result_w_mods:
            self.result_w_mods = result_w_mods
        else: 
            self.result_w_mods = dx_result
        self.nat_one_flag = False
        self.nat_twenty_flag = False
        self.nat_hundred_flag = False

        self.nat_one_flag, self.nat_twenty_flag, self.nat_hundred_flag = self.notable_rolls(dx_type, dx_result)
        return
    
    def notable_rolls(self, dx_type, dx_result):
        if dx_result == 1:
            self.nat_one_flag = True
        
        if dx_result == 20 and dx_type == "d20":
            self.nat_twenty_flag = True
        
        if dx_result == 100 and dx_type == "d100":
            self.nat_hundred_flag = True

        return self.nat_one_flag, self.nat_twenty_flag, self.nat_hundred_flag