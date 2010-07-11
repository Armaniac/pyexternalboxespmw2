from Config import *
from Keys import keys
from ctypes import windll
from structs import ET_PLAYER
import time
import thread

KEYEVENTF_KEYUP = 0x0002

def _stab_glitch():
    windll.User32.keybd_event(ord("E"), 0x12, 0, 0)
    windll.User32.keybd_event(ord("E"), 0x12, KEYEVENTF_KEYUP, 0)
    time.sleep(.16)
    windll.User32.keybd_event(ord("G"), 0x22, 0, 0)
    time.sleep(.03)
    windll.User32.keybd_event(ord("1"), 0x02, 0, 0)
    windll.User32.keybd_event(ord("1"), 0x02, KEYEVENTF_KEYUP, 0)
    time.sleep(.05)
    windll.User32.keybd_event(ord("G"), 0x22, KEYEVENTF_KEYUP, 0)
    time.sleep(.35)

class Autostab(object):
    
    def __init__(self, env):
        self.env = env
        self.last_melee_tick = 0
    
    def stab_glitch(self):
        thread.start_new_thread(_stab_glitch, ())
    
    def get_map_name(self):
        read_game = self.env.read_game
        map_name = read_game.map_name
        if map_name in OFFSET_WEAPON_NUMBERS_MAPS: return True
        else: return False
        
    def is_my_player_tactical(self):
        p = self.env.read_game.my_player
        if self.get_map_name():
            return p.valid and p.alive & 0x0001 and p.weapon_num in KNIFE_TACTICAL_WEAPONS_OFFSET
        else:
            return p.valid and p.alive & 0x0001 and p.weapon_num in KNIFE_TACTICAL_WEAPONS

    def render(self):
        read_game = self.env.read_game
        # Test code for checking my_player weapon number, Is the map we are on an offset map, and the map name.
        # Used for debugging.
        #if keys["KEY_KNIFE_GLITCH"]:
        #    read_game = self.env.read_game
        #    map_name = read_game.map_name
        #    if read_game.is_in_game:
        #        for p in read_game.player:
        #            if p == read_game.my_player:
        #                print p.weapon_num
        #        print self.get_map_name()
        #        print map_name        
        
        if keys["KEY_KNIFE_GLITCH"] and read_game.is_in_game and keys["KEY_RAPID_KNIFE"] and self.is_my_player_tactical():
            if self.env.ticks - self.last_melee_tick > 31:
                self.last_melee_tick = self.env.ticks
                self.stab_glitch()
    
        if not read_game.is_in_game or not keys["KEY_AUTOSTAB"]:
            return
      
        for p in read_game.player:
            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & 0x0001 and p.enemy:
                dist = (p.pos - read_game.my_pos).length()
                vert_dist = abs(p.pos.z - read_game.my_pos.z)
                if dist < AUTOSTAB_DIST and vert_dist < AUTOSTAB_DIST_Z:
                    if keys["KEY_RAPID_KNIFE"] and self.is_my_player_tactical():
                        self.env.ticks - self.last_melee_tick > 27
                        self.last_melee_tick = self.env.ticks
                        self.stab_glitch()
                    else:
                        self.env.ticks - self.last_melee_tick > 10          # surge protector
                        self.last_melee_tick = self.env.ticks
                        windll.User32.keybd_event(0x45, 0x12, 0, 0)
                        windll.User32.keybd_event(0x45, 0x12, KEYEVENTF_KEYUP, 0)