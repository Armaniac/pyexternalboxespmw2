from Config import * #@UnusedWildImport
from Keys import keys
from ctypes import c_float, byref
from directx.types import D3DXVECTOR2, D3DMATRIX
from directx.d3dx import d3dxdll
from structs import VECTOR, ET_PLAYER
from utils import draw_arrow


class BigRadar(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        textures = self.env.textures
        if not read_game.is_in_game or not keys["KEY_BIG_RADAR"]: return
        
        map_name = read_game.map_name
        if map_name not in textures.textures:
            print "map: %s not found" % map_name
            return
        
        scaling = BIG_RADAR_SCALE
        sprite_center = D3DXVECTOR2(0, 0)
        trans = D3DXVECTOR2(read_game.resolution_x - RADAR_OFFSET - 512*scaling, RADAR_OFFSET)

        matrix = D3DMATRIX()
        d3dxdll.D3DXMatrixAffineTransformation2D(byref(matrix), #@UndefinedVariable
                                                 c_float(scaling),          # scaling
                                                 byref(sprite_center),  # rotation center
                                                 c_float(0),        # angle
                                                 byref(trans)           # translation
                                                 )
        
        frame.sprite.Begin(0)
        frame.sprite.SetTransform(matrix)
        frame.sprite.Draw(textures.textures[map_name], None, None, None, BIG_RADAR_BLENDING)
        frame.sprite.End()
        
        pos = read_game.mw2_mypos
        
        matrix = textures.matrix[map_name]
        transl = textures.translations[map_name]
        map_pos = VECTOR()
        map_pos.x = scaling * (transl[0] + matrix[0]*pos.x + matrix[1]*pos.y)
        map_pos.y = scaling * (transl[1] + matrix[2]*pos.x + matrix[3]*pos.y)
        arrow_angle = textures.angle[map_name]
        
        draw_arrow(frame.line, read_game.resolution_x - RADAR_OFFSET - 512*scaling + map_pos.x, RADAR_OFFSET + map_pos.y,
                   -read_game.view_angles.y + arrow_angle, MAP_COLOR_ME);        # myself
        
        for p in read_game.player:
            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & 0x0001:
                pos = p.pos
                map_pos.x = scaling * (transl[0] + matrix[0]*pos.x + matrix[1]*pos.y)
                map_pos.y = scaling * (transl[1] + matrix[2]*pos.x + matrix[3]*pos.y)
                draw_arrow(frame.line, read_game.resolution_x - RADAR_OFFSET - 512*scaling + map_pos.x, RADAR_OFFSET + map_pos.y,
                           -p.yaw + arrow_angle, p.color_map);        # myself
        