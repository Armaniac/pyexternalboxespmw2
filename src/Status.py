import Config
from Config import STATUS_COLOR_ACTIVE, STATUS_COLOR_INACTIVE, KEY_RADAR
from utils import draw_line, draw_string_left
from Keys import keys

#
# draw the status line
#
class Status(object):
    
    def __init__(self, env):
        self.env = env

    def render(self):
        if keys["F1"]:
            frame = self.env.frame
            read_game = self.env.read_game
            draw_line(frame.line, 0, read_game.resolution_y - 10, 845, 0, 20, 0xAF000000)
            
            for i in range(1, 13):
                if keys["F"+str(i)]:
                    color = STATUS_COLOR_ACTIVE
                else:
                    color = STATUS_COLOR_INACTIVE
                label = "F" + str(i) + ":" + getattr(Config, "F"+str(i)+"_LABEL")
                draw_string_left(frame.status_font, (i-1)*70 + 5, read_game.resolution_y-15, 65, 15, color, label)
