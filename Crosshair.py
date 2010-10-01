from Config import * #@UnusedWildImport
from utils import draw_line_abs
from Keys import keys


class Crosshair(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        if not read_game.is_in_game or not keys["KEY_CROSSHAIR"]: return
        
        x = read_game.screen_center_x
        y = read_game.screen_center_y
        draw_line_abs(frame.line, x - CROSSHAIR_SIZE, y, x + CROSSHAIR_SIZE, y, CROSSHAIR_WIDTH, CROSSHAIR_COLOR)
        draw_line_abs(frame.line, x, y - CROSSHAIR_SIZE, x, y + CROSSHAIR_SIZE, CROSSHAIR_WIDTH, CROSSHAIR_COLOR)
