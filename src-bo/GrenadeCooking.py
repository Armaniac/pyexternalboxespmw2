from Config import * #@UnusedWildImport
from Keys import keys
from utils import draw_string_center

class GrenadeCooking(object):
    
    def __init__(self, env):
        self.env = env
        self.reinit()

    def reinit(self):
        self.time_begin_cooking = None

    def render(self):
        read_game = self.env.read_game
        wn = self.env.weapon_names
        frame = self.env.frame
        
        return      # broken
        if not read_game.is_in_game:
            self.reinit()
            return
        
        # is the current lethal weapon "frag grenades"
        frag_active = wn.get_weapon_model(wn.get_frag_grenade()) == "frag_grenade_mp"
        frag_ammo = wn.get_ammo(wn.get_frag_grenade())

        if keys["KEY_GRENADECOOKING_ACTIVE"] and frag_active:
            if keys["KEY_GRENADECOOKING"] and frag_ammo > 0:
                # starting countdown
                self.time_begin_cooking = read_game.game_time
                
            if self.time_begin_cooking is not None:
                # print cooking indicator
                cooking_time = GRENADECOOKING_TIMER - (read_game.game_time - self.time_begin_cooking) / 1000.0
                if cooking_time <= 0:
                    self.reinit()
                else:
                    text = "Cooking: %.1f" % cooking_time 
                    draw_string_center(frame.cooking,
                                       read_game.resolution_x / 2, read_game.resolution_y/2 + GRENADECOOKING_CENTER_Y,
                                       GRENADECOOKING_FONT_COLOR, text)
        else:
            self.reinit()
