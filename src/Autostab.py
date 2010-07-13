from Config import *
from Keys import keys
from ctypes import windll
from structs import ET_PLAYER

KEYEVENTF_KEYUP = 0x0002

class Autostab(object):
    
    def __init__(self, env):
        self.env = env
        self.last_melee_tick = 0
    
    def _stab_glitch(self):                 # coroutine
        read_game = self.env.read_game
        start_time = read_game.game_time
        
        windll.User32.keybd_event(ord("E"), 0x12, 0, 0)
        windll.User32.keybd_event(ord("E"), 0x12, KEYEVENTF_KEYUP, 0)
        while read_game.game_time < start_time + 160:
            yield
        windll.User32.keybd_event(ord("G"), 0x22, 0, 0)
        while read_game.game_time < start_time + 160 + 30:
            yield
        windll.User32.keybd_event(ord("1"), 0x02, 0, 0)
        windll.User32.keybd_event(ord("1"), 0x02, KEYEVENTF_KEYUP, 0)
        while read_game.game_time < start_time + 160 + 30 + 50:
            yield
        windll.User32.keybd_event(ord("G"), 0x22, KEYEVENTF_KEYUP, 0)
    
    def stab_glitch(self):
        self.env.sched.new(self._stab_glitch())
    
    def is_my_player_tactical(self):
        p = self.env.read_game.my_player
        offset = self.env.weapon_names.get_riot_shield_num() - KNIFE_RIOT_OFFSET
        tactical = [ x+offset for x in KNIFE_TACTICAL_WEAPONS ]
        return p.valid and p.alive & 0x0001 and p.weapon_num in tactical

    def render(self):
        read_game = self.env.read_game
        
        if not read_game.is_in_game:    return

        if keys["KEY_RAPID_KNIFE"] and self.is_my_player_tactical():
            if self.env.ticks - self.last_melee_tick > 31:
                self.last_melee_tick = self.env.ticks
                self.stab_glitch()
    
        if keys["KEY_AUTOSTAB"]:
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