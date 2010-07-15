from structs import VECTOR
from ctypes import byref
from Config import *
from utils import draw_arrow
from Keys import keys
from math import radians, cos, sin
from directx.d3d import *
from directx.d3dx import *


class Radar2(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        textures = self.env.textures
        return
        if not read_game.is_in_game: return
        

        scaling = 0.4
        
        pos = read_game.mw2_mypos
        new_pos = VECTOR()
        new_pos.x = scaling * (-pos.y / 11.8 + 212)
        new_pos.y = scaling * (-pos.x / 11.8 + 251)

        sprite_center = D3DXVECTOR2(new_pos.x, new_pos.y)
        trans = D3DXVECTOR2(read_game.resolution_x/2 - new_pos.x, RADAR_OFFSET + RADAR_SIZE/2 - new_pos.y)
        #print "x=%.2f y=%.2f" % (new_pos.x, new_pos.y   )
        angle = radians(read_game.view_angles.y)

        matrix = D3DMATRIX()
        d3dxdll.D3DXMatrixAffineTransformation2D(byref(matrix),
                                                 c_float(scaling),          # scaling
                                                 byref(sprite_center),  # rotation center
                                                 c_float(angle),        # angle
                                                 byref(trans)           # translation
                                                 )
        
        self.sprite.Begin(0)
        self.sprite.SetTransform(matrix)
        self.sprite.Draw(self.texture, None, None, None, 0x7F7FFF7F)
        self.sprite.End()
        
        draw_arrow(frame.line, read_game.resolution_x/2, RADAR_OFFSET + RADAR_SIZE/2, 0, MAP_COLOR_ME);        # myself
        