from ctypes import byref
from Config import * #@UnusedWildImport
from directx.types import D3DRECT, D3DCLEAR
from utils import draw4, draw_line
from Keys import keys


class VisualMouse(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        bot = self.env.bot
        if not read_game.is_in_game or not keys["KEY_BOT_VISUAL_MOUSE"]: return
        
        rx = read_game.resolution_x - VISUAL_MOUSE_SIZE - VISUAL_MOUSE_RIGHT_MARGIN
        ry = read_game.resolution_y - VISUAL_MOUSE_SIZE - VISUAL_MOUSE_BOTTOM_MARGIN
        rh = rw = VISUAL_MOUSE_SIZE
        
        r = D3DRECT(rx, ry, rx + rw, ry + rh)
        frame.device.Clear(1, byref(r), D3DCLEAR.TARGET, VISUAL_MOUSE_COLOR_BACK, 1, 0)
        
        draw4(frame.line, rx, ry, rx+rw, ry, rx+rw, ry+rh, rx, ry+rh, 2, VISUAL_MOUSE_COLOR_BORDER)
        line_x = bot.mouse_move_x
        line_y = bot.mouse_move_x
        if (line_x < -rw/2): line_x = -rw/2
        if (line_x > +rw/2): line_x = +rw/2
        if (line_y < -rh/2): line_y = -rh/2
        if (line_y > +rh/2): line_y = +rh/2
        
        draw_line(frame.line, int(rx + rw/2), int(ry + rh/2), line_x, line_y, VISUAL_MOUSE_LINE_WIDTH, VISUAL_MOUSE_COLOR_LINE)
