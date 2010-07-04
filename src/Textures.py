import win32api, win32con, win32gui
from directx.d3d import IDirect3DTexture9
from directx.d3dx import d3dxdll
from ctypes import POINTER, byref
import math
from structs import COORD
import os

MAP_FOLDER = "maps\\"
MAP_EXT = ".jpg"
# map_name => first point in game, first point coord on pic (512*512), same for 2nd point
MAP_NAMES = { "mp_afghan": ((4388,940), (296,32), (-715,1196), (276,412)),
              "mp_boneyard": ((1969,-625), (353,75), (-1756,1664), (126,448)),
              "mp_brecourt": ((3924,-2705), (368,106), (-3796,1614), (166,467)),
              "mp_checkpoint": ((793,2329), (15,184), (103,-3457), (505,243)),
              "mp_compact": ((4198,2153), (136,56), (497,-369), (385,420)),
              "mp_complex": ((-2865,-2665), (260,495), (2814,-3596), (363,30)),
              "mp_crash": ((-753,2277), (26,380), (753,-2129), (508,216)),
              "mp_derail": ((407,4439), (65,266), (-1105,-3697), (444,337)),
              "mp_estate": ((1991,443), (301,463), (-5077,3781), (219,27)),
              "mp_favela": ((-1593,-246), (363,401), (953,2899), (68,163)),
              "mp_highrise": ((1649,7271), (183,34), (-3905,5529), (328,488)),
              "mp_invasion": ((-3039,-2969), (332,452), (1042,-395), (124,120)),
              "mp_nightshift": ((1544,-1752), (369,92), (-1536,944), (123,371)),
              "mp_overgrown": ((-413,808), (9,288), (-1955,-5308), (504,412)),
              "mp_quarry": ((-5400,-2067), (483,371), (-1815,3072), (75,87)),
              "mp_rundown": ((1764,3359), (17,151), (1999,-3557), (512,133)),
              "mp_rust": ((-468,-224), (427,405), (1640,1808), (158,125)),
              "mp_storm": ((-2408,112), (236,495), (2536,-1328), (377,11)),
              "mp_subbase": ((-488,-3816), (483,339), (2592,1840), (11,83)),
              "mp_terminal": ((1569,2447), (504,218), (1476,7520), (10,227)),
              "mp_underpass": ((-600,-1232), (460,472), (2600,3440), (37,183)),
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
                d3dxdll.D3DXCreateTextureFromFileA(frame.device,
                                                  MAP_FOLDER + m + MAP_EXT,
                                                  byref(texture))
                self.textures[m] = texture
                # now calculate transformations
                len_game = math.hypot(l[0][0] - l[2][0], l[0][1] - l[2][1])
                len_pict = math.hypot(l[1][0] - l[3][0], l[1][1] - l[3][1])
                k = len_pict / len_game
                # matrix in form ((a,b) (c,d)) -> (a,b,c,d)
                matr = (0, -k, -k, 0)
                self.angle[m] = 0
                if m in ("mp_estate"):
                    alpha = math.radians(35.9)
                    sa = k * math.sin(alpha)
                    ca = k * math.cos(alpha)
                    matr = (sa, ca, ca, -sa)
                    self.angle[m] = 180-35.9
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