from Config import * #@UnusedWildImport
from utils import draw_string_center
from Keys import keys

class Killstreak(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        if not read_game.is_in_game or not keys["KEY_KILLSTREAK"] or read_game.killstreak < 0: return
        
        text = "%i" % read_game.killstreak
        if keys["KEY_BIG_RADAR"]:
            draw_string_center(frame.killstreak_font, read_game.resolution_x - 52 - 512*BIG_RADAR_SCALE, 70, KILLSTREAK_FONT_COLOR, text)       
        else:
            draw_string_center(frame.killstreak_font, read_game.resolution_x - 100, 70, KILLSTREAK_FONT_COLOR, text)         