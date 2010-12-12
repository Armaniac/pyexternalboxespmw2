from Config import * #@UnusedWildImport
from Keys import keys
from ctypes import c_float, byref
from directx.types import D3DXVECTOR2, D3DMATRIX
from directx.d3dx import d3dxdll
from structs import VECTOR, ET_PLAYER, ET_TURRET, ET_HELICOPTER, ET_PLANE, ET_EXPLOSIVE, ALIVE_FLAG
from utils import draw_arrow


class BigRadar(object):
    
    def __init__(self, env):
        self.env = env
        self.scaling = BIG_RADAR_SCALE
        self.rx = 0
        self.ry = 0
        self.rh = 0
        self.rw = 0
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        textures = self.env.textures
        if not read_game.is_in_game or not keys["KEY_BIG_RADAR"]: return
        
        map_name = read_game.map_name
        if map_name not in textures.textures:
            #print "map: %s not found" % map_name
            return
        
        rx = self.rx = read_game.resolution_x - RADAR_OFFSET - 512*self.scaling
        ry = self.rx = RADAR_OFFSET
        rh = self.rh = 512*self.scaling
        rw = self.rw = 512*self.scaling
        
        sprite_center = D3DXVECTOR2(0, 0)
        trans = D3DXVECTOR2(rx, ry)

        matrix = D3DMATRIX()
        d3dxdll.D3DXMatrixAffineTransformation2D(byref(matrix), #@UndefinedVariable
                                                 c_float(self.scaling),          # scaling
                                                 byref(sprite_center),  # rotation center
                                                 c_float(0),        # angle
                                                 byref(trans)           # translation
                                                 )
        
        frame.sprite.Begin(0)
        frame.sprite.SetTransform(matrix)
        frame.sprite.Draw(textures.textures[map_name], None, None, None, BIG_RADAR_BLENDING)
        frame.sprite.End()
        
        matrix = textures.matrix[map_name]
        transl = textures.translations[map_name]
        map_pos = VECTOR()
        arrow_angle = textures.angle[map_name]
        arrow_inversion = textures.angle_inversion[map_name]
        
        for te in self.env.tracker.get_tracked_entity_list():
            x = self.scaling * (transl[0] + matrix[0]*te.pos.x + matrix[1]*te.pos.y)
            y = self.scaling * (transl[1] + matrix[2]*te.pos.x + matrix[3]*te.pos.y)
            if x < 0:               x = 0
            if x > rw:              x = rw
            if y < 0:               y = 0
            if y > rh:              y = rh               
            if te.type == ET_TURRET:
                self.env.sprites.draw_sentry(rx + x, ry + y, te.planter.enemy)
            if te.type == ET_HELICOPTER:
                self.env.sprites.draw_heli(rx + x, ry + y, -te.yaw + arrow_angle + arrow_inversion, te.planter.enemy, te.weapon_num)
            if te.type == ET_PLANE:
                self.env.sprites.draw_plane(rx + x, ry + y, -te.yaw + arrow_angle + arrow_inversion, te.planter.enemy)
            if te.type == ET_EXPLOSIVE and te.model_name.find("_AIRDROP_") > 0:
                self.env.sprites.draw_flare(rx + x, ry + y)
        
        pos = read_game.my_pos
        map_pos.x = self.scaling * (transl[0] + matrix[0]*pos.x + matrix[1]*pos.y)
        map_pos.y = self.scaling * (transl[1] + matrix[2]*pos.x + matrix[3]*pos.y)
        draw_arrow(frame.line, rx + map_pos.x, ry + map_pos.y,
                   -read_game.view_angles.y + arrow_angle, MAP_COLOR_ME);        # myself
        
        for p in read_game.player:
            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & ALIVE_FLAG:
                map_pos.x = self.scaling * (transl[0] + matrix[0]*p.pos.x + matrix[1]*p.pos.y)
                map_pos.y = self.scaling * (transl[1] + matrix[2]*p.pos.x + matrix[3]*p.pos.y)
                draw_arrow(frame.line, rx + map_pos.x, ry + map_pos.y,
                           -p.yaw + arrow_angle + arrow_inversion, p.color_map);        # myself
        