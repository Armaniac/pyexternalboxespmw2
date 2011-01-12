from Config import * #@UnusedWildImport
from Keys import keys
from ctypes import windll
from structs import ET_PLAYER, ALIVE_FLAG

KEYEVENTF_KEYUP = 0x0002

class Autostab(object):
    
    def __init__(self, env):
        self.env = env
        self.last_melee_tick = 0

    def render(self):
        read_game = self.env.read_game
        
        if not read_game.is_in_game:    return
    
        if keys["KEY_AUTOSTAB"] and read_game.my_player.alive & ALIVE_FLAG:
            autostab_dist = AUTOSTAB_DIST
            if keys["KEY_AUTOSTAB_RUN"]:
                autostab_dist = AUTOSTAB_DIST_RUN
            for p in read_game.player:
                if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & ALIVE_FLAG and p.enemy:
                    dist = (p.pos - read_game.my_pos).length()
                    vert_dist = abs(p.pos.z - read_game.my_pos.z)
                    if dist < autostab_dist and vert_dist < AUTOSTAB_DIST_Z:
                        if self.env.ticks - self.last_melee_tick > 10:          # surge protector
                            self.last_melee_tick = self.env.ticks
                            windll.User32.keybd_event(ord(AUTOSTAB_KEY), 0x12, 0, 0)
                            windll.User32.keybd_event(ord(AUTOSTAB_KEY), 0x12, KEYEVENTF_KEYUP, 0)