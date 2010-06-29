from structs import ET_PLAYER, PLAYERMAX
from Config import *
from Keys import keys
from utils import draw_string_center

# this module affects a special color to an enemy you want to rage
# you can then easily spot it both on radar and ESP
# It only changes the color, no impact on aimbot

class Rage(object):
    
    def __init__(self, env):
        self.env = env
        self.rage_player_index = -1
    
    def render(self):
        frame = self.env.frame
        read_game = self.env.read_game
        
        if not read_game.is_in_game:
            self.rage_player_index = -1
            return
        
        do_next = keys["KEY_RAGE_NEXT"]
        do_prev = keys["KEY_RAGE_PREV"]
        do_reset = keys["KEY_RAGE_RESET"]
        
        if do_next or do_prev:
            idx = self.rage_player_index          # player index or 0 if negative
            if do_next: incr = 1
            else:       incr = -1 
            for i in range(PLAYERMAX):
                idx += incr
                if idx >= PLAYERMAX:    idx = 0
                if idx < 0:             idx = PLAYERMAX - 1
                p = read_game.player[idx]
                if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & 0x0001 and p.enemy:
                    self.rage_player_index = idx
                    break
            else:
                self.rage_player_index = -1             # none found
        elif do_reset:
            if self.rage_player_index >= 0:
                self.rage_player_index = -1
                draw_string_center(frame.rage_font, read_game.screen_center_x, read_game.screen_center_y + 40, RAGE_FONT_COLOR, RAGE_RESET_STRING)
        # display player name in HUD display?
        
        if keys["KEY_RAGE_DISPLAY_NAME"] and self.rage_player_index >= 0:
            draw_string_center(frame.rage_font, read_game.screen_center_x, read_game.screen_center_y + 40, RAGE_FONT_COLOR, read_game.player[self.rage_player_index].name)
            

        
        # now display player
        if self.rage_player_index >= 0:
            p = read_game.player[self.rage_player_index]
            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & 0x0001 and p.enemy:
                p.color_esp = RAGE_COLOR_ESP
                p.color_map = RAGE_COLOR_MAP
        