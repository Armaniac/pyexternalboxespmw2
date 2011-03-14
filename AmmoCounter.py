from Config import * #@UnusedWildImport
from utils import draw_string_center

DUAL_WEAPON = "dw_"
LEFT_HAND = "lh_"

class AmmoCounter(object):
    
    def __init__(self, env):
        self.env = env

    def render(self):
        read_game = self.env.read_game
        wn = self.env.weapon_names
        frame = self.env.frame
        
        if not read_game.is_in_game:    return
        if wn.weapon_models is None:    return

        cur_wp = wn.get_current_weapon()
        weapon_model = wn.get_weapon_model(cur_wp)
        ammo_str = "%i" % wn.get_ammo(cur_wp)
        if weapon_model.find(DUAL_WEAPON) > 0:      # check if dual weapon
            lh_model = weapon_model.replace(DUAL_WEAPON, LEFT_HAND)
            # look for previous or next weapon
            if wn.get_weapon_model(cur_wp - 1) == lh_model:
                ammo_str = "%i/%i" % (wn.get_ammo(cur_wp), wn.get_ammo(cur_wp - 1))
            elif wn.get_weapon_model(cur_wp + 1) == lh_model:
                ammo_str = "%i/%i" % (wn.get_ammo(cur_wp), wn.get_ammo(cur_wp + 1))
        draw_string_center(frame.rage_font,
                           read_game.resolution_x - AMMO_COUNTER_MARGIN_RIGHT,
                           read_game.resolution_y - AMMO_COUNTER_MARGIN_BOTTOM,
                           AMMO_COUNTER_BACK_COLOR, ammo_str)
        draw_string_center(frame.rage_font,
                           read_game.resolution_x - AMMO_COUNTER_MARGIN_RIGHT - AMMO_COUNTER_BACK_OFFSET,
                           read_game.resolution_y - AMMO_COUNTER_MARGIN_BOTTOM - AMMO_COUNTER_BACK_OFFSET,
                           AMMO_COUNTER_TEXT_COLOR, ammo_str)
