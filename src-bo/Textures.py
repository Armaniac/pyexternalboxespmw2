from directx.d3d import IDirect3DTexture9
from directx.d3dx import d3dxdll
from ctypes import POINTER, byref
import math
import os

MAP_FOLDER = "maps\\"
MAP_EXT = ".png"
# map_name => first point in game, first point coord on pic (512*512), same for 2nd point
MAP_NAMES = { "mp_array": ((-1836,3869), (41,361), (979,-2809), (464,181)),
              "mp_cracked": ((-3450,-990), (276,480), (816,1208), (83,120)),
              "mp_crisis": ((-3230,478), (296,472), (3194,2527), (159,50)),
              "mp_firingrange": ((2680,1688), (182,58), (-746,-884), (430,388)),
              "mp_duga": ((-2220,-842), (81,342), (-662,-6082), (436,236)),
              "mp_hanoi": ((-2487,-2503), (385,431), (2132,1184), (77,45)),
              "mp_cairo": ((-1875,-637), (304,470), (2736,344), (208,32)),
              "mp_havoc": ((-739,-736), (261,375), (3365,-1107), (284,113)),
              "mp_cosmodrome": ((408,3920), (13,243), (416,-2940), (482,243)),
              "mp_nuked": ((-1638,1211), (170,416), (2092,162), (273,46)),
              "mp_radiation": ((-1328,-2448), (470,342), (1129,2360), (69,137)),
              "mp_mountain": ((2450,1960), (229,87), (3743,-3277), (318,453)),
              "mp_villa": ((4310,4776), (29,185), (2036,-1056), (465,355)),
              "mp_russianbase": ((2360,904), (206,44), (-2416,-464), (333,467)),
              # dlc
              "mp_berlinwall2": ((-2363,-456), (249,418), (2413,-859), (275,84)),
              "mp_discovery": ((-571,2835), (69,219), (108,-3369), (497,174)),
              "mp_kowloon": ((2745,2348), (84,38), (-2160,-976), (363,452)),
              "mp_stadium": ((-544,4400), (36,294), (-1776,-256), (421,398)),
              # dlc 2
              "mp_gridlock": ((-2387,645), (246,430), (2569,-139), (305,69)),
              "mp_hotel": ((-444,-876), (270,436), (6576,84), (218,67)),
              "mp_outskirts": ((-2280,-1386), (356,446), (3058,733), (204,66)),
              "mp_zoo": ((676,-1892), (422,209), (-487,3602), (66,286)),
              # dlc 3
              "mp_drivein": ((-1008,-3319), (205,474), (724,3572), (312,41)),
              "mp_area51": ((-868,2504), (209,26), (-690,-3054), (224,484)),
              "mp_golfcourse": ((-632,-2081), (395,166), (-4424,734), (204,420)),
              "mp_silo": ((2888,-234), (324,41), (-2408,-1112), (387,432)),
             }

class Textures(object):
    
    def __init__(self, env):
        self.env = env
        self.textures = {}
        self.matrix = {}
        self.translations = {}
        self.angle = {}             # map rotation, 0 for all maps except estate
        self.angle_inversion = {}   # need to invert arrow in estate, 0 if no inversion, 180 otherwise

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
                sa = k * math.sin(math.radians(delta))
                ca = k * math.cos(math.radians(delta))
                matr = (sa, -ca, -ca, -sa)
                self.angle[m] = delta
                self.matrix[m] = matr
                self.angle_inversion[m] = 0.0
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