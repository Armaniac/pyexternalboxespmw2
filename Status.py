import Config
from Config import STATUS_COLOR_ACTIVE, STATUS_COLOR_INACTIVE, STATUS_COLOR_LINE, FPS_VIEWER_INTERVAL
from utils import draw_line, draw_string_left, draw_string_center
from Keys import keys, keys_raw, KEY_TOGGLE
import vk_codes

#
# draw the status line
#

class Status(object):
    
    def __init__(self, env):
        self.env = env
        self.fps = -1
        self.fps_count = -1                      # tick counter for FPS calculation
        self.fps_time = 0
    
    def render(self):
        frame = self.env.frame
        read_game = self.env.read_game
        
        if keys["KEY_STATUS"]:
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
                draw_string_center(frame.rage_font, read_game.resolution_x - 250, read_game.resolution_y - 10, 0xA0FFFF00, weapon_model)

        if keys["KEY_FPS_VIEWER"]:
            self.calc_fps()
            if self.fps > 0:
                draw_string_center(frame.rage_font, read_game.resolution_x - 50, read_game.resolution_y - 10, 0xA0FFFF00, "FPS=%.0f" % self.fps)
        else:
            self.reset_fps()

    def calc_fps(self):
        self.fps_count += 1
        
        if self.fps_count == 0:
            self.fps_time = self.env.time
        
        if self.fps_count == FPS_VIEWER_INTERVAL:
            if (self.env.time > self.fps_time):
                self.fps =  float(FPS_VIEWER_INTERVAL) / (self.env.time - self.fps_time)
            else:
                self.fps = -1           # invalid
            self.fps_count = -1
        
    def reset_fps(self):
        self.fps = -1
        self.fps_count = -1                      # tick counter for FPS calculation
        self.fps_time = 0
        