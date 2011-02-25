from Config import * #@UnusedWildImport
from Keys import keys
from ctypes import windll
from structs import ET_PLAYER, ALIVE_FLAG, ET_EXPLOSIVE
from utils import draw_string_right, draw_string_center

KEYEVENTF_KEYUP = 0x0002

class C4AutoFire(object):
    
    def __init__(self, env):
        self.env = env
        self.last_melee_tick = 0

    def render(self):
        read_game = self.env.read_game
        wn = self.env.weapon_names
        frame = self.env.frame
        
        if not read_game.is_in_game:    return
        
        # first check if we own a C4
        
        if keys["KEY_C4AUTOFIRE"] and read_game.my_player.alive & ALIVE_FLAG:
            c4_autofire_active = False
            for te in self.env.tracker.get_tracked_entity_list():
                if te.type == ET_EXPLOSIVE and wn.get_weapon_model(te.weapon_num) == "satchel_charge_mp":
                    if te.planter is read_game.my_player:
                        # this is my C4
                        c4_autofire_active = True
                        for p in read_game.player:
                            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & ALIVE_FLAG and p.enemy:
                                dist = (p.pos - te.pos).length()
                                vert_dist = abs(p.pos.z - te.pos.z)
                                if dist < C4AUTOFIRE_DIST and vert_dist < C4AUTOFIRE_DIST_Z:
                                    if self.env.ticks - self.last_melee_tick > 10:          # surge protector
                                        self.last_melee_tick = self.env.ticks
                                        # launch double-tap
                                        windll.User32.keybd_event(ord(C4AUTOFIRE_DOUBLETAP_KEY), 0x12, 0, 0)
                                        windll.User32.keybd_event(ord(C4AUTOFIRE_DOUBLETAP_KEY), 0x12, KEYEVENTF_KEYUP, 0)
                                        windll.User32.keybd_event(ord(C4AUTOFIRE_DOUBLETAP_KEY), 0x12, 0, 0)
                                        windll.User32.keybd_event(ord(C4AUTOFIRE_DOUBLETAP_KEY), 0x12, KEYEVENTF_KEYUP, 0)
                                        return
            if c4_autofire_active and keys["KEY_C4AUTOFIRE_DISPLAY"]:
                draw_string_right(frame.c4_font,
                                  read_game.resolution_x - C4AUTOFIRE_CENTER_RIGHT_X - 2,
                                  read_game.resolution_y/2 + C4AUTOFIRE_CENTER_Y,
                                  150, 10,
                                  C4AUTOFIRE_FONT_COLOR, C4AUTOFIRE_MESSAGE)