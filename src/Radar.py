from structs import ET_PLAYER, VECTOR
from ctypes import byref
from Config import *
from directx.types import D3DRECT, D3DCLEAR
from utils import draw_arrow, draw4, draw_spot
from Keys import keys
from math import radians, cos, sin


class Radar(object):
    
    def __init__(self, env):
        self.env = env
        self.rx = 0
        self.ry = 0
        self.rh = 0
        self.rw = 0
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        if not read_game.is_in_game or not keys["KEY_RADAR"]: return
        
        rx = self.rx = int(read_game.resolution_x/2 - RADAR_SIZE/2)
        ry = self.ry = RADAR_OFFSET
        rh = rw = self.rh = self.rw = RADAR_SIZE
        
        r = D3DRECT(rx, ry, rx + rw, ry + rh)
        frame.device.Clear(1, byref(r), D3DCLEAR.TARGET, MAP_COLOR_BACK, 1, 0)


        
        draw4(frame.line, rx, ry, rx+rw, ry, rx+rw, ry+rh, rx, ry+rh, 2, MAP_COLOR_BORDER)

        draw_arrow(frame.line, rx + rw/2, ry + rh/2, 0, MAP_COLOR_ME);        # myself
        
        for p in read_game.player:
            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & 0x0001:
                cx, cy = self.calcPoint(p.pos, RADAR_RANGE)
                draw_arrow(frame.line, cx, cy, -p.yaw + read_game.view_angles.y, p.color_map);
        
        # clibrating is a debug mode
        if CALIBRATING:
            origin = VECTOR(0, 0, 0)
            cx, cy = self.calcPoint(origin, RADAR_RANGE)
            draw_spot(frame.line, cx, cy, 0x7FFFFFFF)
        
    def calcPoint(self, vec, range):
        read_game = self.env.read_game

        fy = radians(read_game.view_angles.y)
        fc = cos(fy)
        fs = sin(fy)
        dx = vec.x - read_game.my_pos.x
        dy = vec.y - read_game.my_pos.y
        px = dy * ( -fc ) + ( dx * fs )
        py = dx * ( -fc ) - ( dy * fs )
        irrx = ( self.rx + ( self.rw / 2 ) ) + int( px / range )
        irry = ( self.ry + ( self.rh / 2 ) ) + int( py / range )
        
        if irrx < self.rx:              irrx = self.rx
        if irry < self.ry:              irry = self.ry
        if irrx > self.rx + self.rw:    irrx = self.rx + self.rw
        if irry > self.ry + self.rh:    irry = self.ry + self.rh
        return (irrx, irry)
