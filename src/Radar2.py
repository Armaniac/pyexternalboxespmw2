from structs import VECTOR, ET_PLAYER
from Config import * #@UnusedWildImport
from utils import draw_arrow, draw4
from Keys import keys
from math import radians
from ctypes import byref, c_float
from directx.d3d import D3DRECT, D3DCLEAR, RECT
from directx.d3dx import d3dxdll, D3DXVECTOR2, D3DMATRIX


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
        textures = self.env.textures

        if not read_game.is_in_game or not keys["KEY_RADAR"]: return
        
        rx = self.rx = int(read_game.resolution_x/2 - RADAR_SIZE/2 + RADAR_CENTER_X)
        ry = self.ry = RADAR_OFFSET
        rh = rw = self.rh = self.rw = RADAR_SIZE
        
        
        scaling = 0.5           # TODO
        
        pos = read_game.mw2_mypos
        
        map_name = read_game.map_name               # name of the current map
        p_matrix = textures.matrix[map_name]          # transformation matrix (scale + rotation)
        transl = textures.translations[map_name]    # translation vector to correct with map origin
        map_pos = VECTOR()                          # contains the coord on the map (with applied scaling)
        map_pos.x = scaling * (transl[0] + p_matrix[0]*pos.x + p_matrix[1]*pos.y)
        map_pos.y = scaling * (transl[1] + p_matrix[2]*pos.x + p_matrix[3]*pos.y)
        arrow_angle = textures.angle[map_name]      # offset to apply to angles (only in estate)s
        
        sprite_center = D3DXVECTOR2(map_pos.x, map_pos.y)
        trans = D3DXVECTOR2(read_game.resolution_x/2 - map_pos.x, RADAR_OFFSET + RADAR_SIZE/2 - map_pos.y)   # global translation
        #print "x=%.2f y=%.2f" % (new_pos.x, new_pos.y   )
        angle = radians(read_game.view_angles.y)
        
        matrix = D3DMATRIX()
        d3dxdll.D3DXMatrixAffineTransformation2D(byref(matrix), #@UndefinedVariable
                                                 c_float(scaling),          # scaling
                                                 byref(sprite_center),  # rotation center
                                                 c_float(angle),        # angle
                                                 byref(trans)           # translation
                                                 )
        
        r = D3DRECT(rx, ry, rx + rw, ry + rh)
        frame.device.Clear(1, byref(r), D3DCLEAR.TARGET, MAP_COLOR_BACK, 1, 0)
        if keys["KEY_RADAR_MAP"]:
            frame.device.SetRenderState(174, True)
            save_scissors = None
            try:
                save_scissors = RECT()
                frame.device.GetScissorRect(byref(save_scissors))
                scissors = RECT(rx, ry, rx+rw, ry+rh)
                frame.device.SetScissorRect(byref(scissors))
            except:
                pass
                
            
            frame.sprite.Begin(0)
            frame.sprite.SetTransform(matrix)
            frame.sprite.Draw(textures.textures[map_name], None, None, None, BIG_RADAR_BLENDING)
            frame.sprite.Flush()
            frame.sprite.End()
            
            frame.device.SetRenderState(174, False)
            
            if not save_scissors is None:
                frame.device.SetScissorRect(byref(save_scissors))
                
        draw4(frame.line, rx, ry, rx+rw, ry, rx+rw, ry+rh, rx, ry+rh, 2, MAP_COLOR_BORDER)
        draw_arrow(frame.line, rx + rw/2, ry + rh/2, 0, MAP_COLOR_ME);        # myself
        
        p_pos = VECTOR()
        for p in read_game.player:
            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & 0x0001:
                p_pos.x = transl[0] + p_matrix[0]*p.pos.x + p_matrix[1]*p.pos.y
                p_pos.y = transl[1] + p_matrix[2]*p.pos.x + p_matrix[3]*p.pos.y
                cx, cy = self.calcPoint(p_pos, matrix)
                #print "pos=%.1f %.1f, p_pos=%.1f %.1f, cxy=%.1f %.1f" % (p.pos.x, p.pos.y, p_pos.x, p_pos.y, cx, cy)
                draw_arrow(frame.line, cx, cy, -p.yaw + read_game.view_angles.y, p.color_map);
        
    def calcPoint(self, vec, mat):
        ir = self.vec2transform(vec, mat)
        if ir.x < self.rx:              ir.x = self.rx
        if ir.y < self.ry:              ir.y = self.ry
        if ir.x > self.rx + self.rw:    ir.x = self.rx + self.rw
        if ir.y > self.ry + self.rh:    ir.y = self.ry + self.rh
        return (ir.x, ir.y)
    
    def vec2transform(self, vec, mat):      # accepts D3DXVECTOR2 and D3DXMATRIX, returns D3DXVECTOR2
        res = D3DXVECTOR2()
        d3dxdll.D3DXVec2TransformCoord(byref(res), byref(vec), byref(mat))
        return res 
        return D3DXVECTOR2(vec.x * mat.m[0] + vec.y * mat.m[1] + mat.m[3],
                           vec.x * mat.m[4] + vec.y * mat.m[5] + mat.m[7])
