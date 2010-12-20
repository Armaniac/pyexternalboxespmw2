import Config
from Config import STATUS_COLOR_ACTIVE, STATUS_COLOR_INACTIVE, STATUS_COLOR_LINE
from utils import draw_line, draw_string_left, draw_string_center
from Keys import keys, keys_raw, KEY_TOGGLE
import vk_codes

#
# draw the status line
#

class Status(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        if not keys["KEY_STATUS"]: return
        frame = self.env.frame
        read_game = self.env.read_game
        
        if keys["KEY_STATUS_UP"]:
            draw_line(frame.line, 0, 9, 845, 0, 20, STATUS_COLOR_LINE)
            text_y = 3
        else:
            draw_line(frame.line, 0, read_game.resolution_y - 10, 845, 0, 20, STATUS_COLOR_LINE)
            text_y = read_game.resolution_y-15

        for i in range(1, 13):
            if keys_raw[vk_codes.VK_F1+i-1] & KEY_TOGGLE:
                color = STATUS_COLOR_ACTIVE
            else:
                color = STATUS_COLOR_INACTIVE
            label = "F" + str(i) + ":" + getattr(Config, "F"+str(i)+"_LABEL")
            draw_string_left(frame.status_font, (i-1)*70 + 5, text_y, 65, 15, color, label)
        
        if read_game.is_in_game and keys["KEY_INSPECT_WEAPON_NAME"]:
            weapon_model = self.env.weapon_names.get_weapon_model(self.env.read_game.my_player.weapon_num)
            if weapon_model is not None:
                draw_string_center(frame.rage_font, read_game.resolution_x - 100, read_game.resolution_y - 10, 0xA0FFFF00, weapon_model)   
