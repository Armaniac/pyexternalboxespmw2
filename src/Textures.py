from directx.d3d import IDirect3DTexture9
from directx.d3dx import d3dxdll
from ctypes import POINTER, byref
import math
import os

MAP_FOLDER = "maps\\"
MAP_EXT = ".jpg"
# map_name => first point in game, first point coord on pic (512*512), same for 2nd point
MAP_NAMES = { "mp_abandon": ((3638,728), (187,36), (-1260,-925), (332,471)),
              "mp_afghan": ((4388,940), (296,32), (-715,1196), (276,412)),
              "mp_boneyard": ((1969,-625), (353,75), (-1756,1664), (126,448)),
              "mp_brecourt": ((3924,-2705), (368,106), (-3796,1614), (166,467)),
              "mp_checkpoint": ((793,2329), (15,184), (103,-3457), (505,243)),
              "mp_compact": ((4198,2153), (136,56), (497,-369), (385,420)),
              "mp_complex": ((2760,-2283), (230,32), (-2864,-2664), (259,495)),
              "mp_crash": ((-753,2277), (26,380), (753,-2129), (508,216)),
              "mp_derail": ((407,4439), (65,266), (-1105,-3697), (444,337)),
              "mp_estate": ((1991,443), (301,463), (-5077,3781), (219,27)),
              "mp_favela": ((-1593,-246), (363,401), (953,2899), (68,163)),
              "mp_fuel2": ((-2217,1445), (136,452), (4324,-487), (268,12)),
              "mp_highrise": ((1649,7271), (183,34), (-3905,5529), (328,488)),
              "mp_invasion": ((-3039,-2969), (332,452), (1042,-395), (124,120)),
              "mp_nightshift": ((1544,-1752), (369,92), (-1536,944), (123,371)),
              "mp_overgrown": ((-413,808), (9,288), (-1955,-5308), (504,412)),
              "mp_quarry": ((-5400,-2067), (483,371), (-1815,3072), (75,87)),
              "mp_rundown": ((1764,3359), (17,151), (1999,-3557), (512,133)),
              "mp_rust": ((-468,-224), (427,405), (1640,1808), (158,125)),
              "mp_storm": ((-2408,112), (236,495), (2536,-1328), (377,11)),
              "mp_strike": ((-1592,-3104), (483,404), (3358,2822), (21,18)),
              "mp_subbase": ((-488,-3816), (483,339), (2592,1840), (11,83)),
              "mp_terminal": ((1569,2447), (504,218), (1476,7520), (10,227)),
              "mp_trailerpark": ((2027,-987), (322,26), (-2535,1308), (110,447)),
              "mp_underpass": ((-600,-1232), (460,472), (2600,3440), (37,183)),
              "mp_vacant": ((1646,-944), (400,10), (-2088,1416), (108,474)),
             }
class Textures(object):
    
    def __init__(self, env):
        self.env = env
        self.textures = {}
        self.matrix = {}
        self.translations = {}
        self.angle = {}        # need to invert arrow in estate

    def init(self):
        frame = self.env.frame
        
        if os.path.isdir(MAP_FOLDER):
            for (m, l) in MAP_NAMES.items():
                texture = POINTER(IDirect3DTexture9)()
                d3dxdll.D3DXCreateTextureFromFileA(frame.device, #@UndefinedVariable
                                                  MAP_FOLDER + m + MAP_EXT,
                                                  byref(texture))
                self.textures[m] = texture
                # now calculate transformations
                len_game = math.hypot(l[0][0] - l[2][0], l[0][1] - l[2][1])
                len_pict = math.hypot(l[1][0] - l[3][0], l[1][1] - l[3][1])
                k = len_pict / len_game
                angle1 = math.atan2(l[2][1] - l[0][1], l[2][0] - l[0][0])
                angle2 = math.atan2(l[3][1] - l[1][1], l[3][0] - l[1][0])
                delta = math.degrees(angle2 + angle1) + 90
                if delta > 180.0:  delta -= 360.0
                if delta > -1.0 and delta < 1.0:    delta = 0.0         # small angles are considered as zero
                # matrix in form ((a,b) (c,d)) -> (a,b,c,d)
                sa = k * math.sin(delta)
                ca = k * math.cos(delta)
                matr = (sa, -ca, -ca, -sa)
                self.angle[m] = delta
                self.matrix[m] = matr
                # now calculate translation
                new_x = matr[0]*l[0][0] + matr[1]*l[0][1]
                new_y = matr[2]*l[0][0] + matr[3]*l[0][1]
                transl = (l[1][0] - new_x, l[1][1] - new_y)
                self.translations[m] = transl
        else:
            print "'maps' folder is not present!\nThis folder and the maps it contains are needed to display map radar."
    
    def render(self):
        pass

if __name__ == "__main__":
    for (map, coord) in MAP_NAMES.items():
        angle1 = math.atan2(coord[2][1] - coord[0][1], coord[2][0] - coord[0][0])
        angle2 = math.atan2(coord[3][1] - coord[1][1], coord[3][0] - coord[1][0])
        delta = math.degrees(angle2 + angle1) + 90
        if delta > 180.0:  delta -= 360.0
        print "map=%s, delta angle=%.2f" % (map, delta)
    
#    textures = Textures(None)
#    textures.init()
#    for (map, matrix) in textures.matrix.items():
#        print "map=%s, matrix=%s" % (map, matrix)