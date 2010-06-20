from ctypes import *
from UserList import UserList
import math

class Rect(UserList):
    def __init__(self, initlist=None):
        super(Rect, self).__init__(initlist)
        self.left = initlist[0]
        self.top = initlist[1]
        self.right = initlist[2]
        self.bottom = initlist[3]    

PLAYERMAX = 18            # number of players to loop in
ENTITIESMAX = 2048        # total number of entities present

ET_GENERAL          = 0
ET_PLAYER           = 1
ET_PLAYER_CORPSE    = 2
ET_ITEM             = 3
ET_EXPLOSIVE        = 4
ET_INVISIBLE        = 5
ET_SCRIPTMOVER      = 6
ET_SOUND_BLEND      = 7
ET_FX               = 8
ET_LOOP_FX          = 9
ET_PRIMARY_LIGHT    = 10
ET_TURRET           = 11
ET_HELICOPTER       = 12
ET_PLANE            = 13
ET_VEHICLE          = 14
ET_VEHICLE_COLLMAP  = 15
ET_VEHICLE_CORPSE   = 16
ET_VEHICLE_SPAWNER  = 17

FLAGS_CROUCHED      = 0x0004
FLAGS_PRONE         = 0x0008
FLAGS_FIRING        = 0x0200 


# memory structures
class VECTOR(Structure):
    _fields_ = [ ("x", c_float),
                 ("y", c_float),
                 ("z", c_float) ]
    
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    def dotProduct(self, dot):
        return self.x*dot.x + self.y*dot.y + self.z*dot.z;
    def __add__(self, other):
        return VECTOR(self.x+other.x, self.y+other.y, self.z+other.z)
    def __sub__(self, other):
        return VECTOR(self.x-other.x, self.y-other.y, self.z-other.z)

class COORD(Structure):
    _fields_ = [ ("x", c_float),
                 ("y", c_float) ]
    
class MW2_RefDef(Structure):
    _fields_ = [ ("_p00", c_char * 16),
                 ("fov_x", c_float),
                 ("fov_y", c_float),
                 ("_P01", c_char * 12),
                 ("viewAxis", VECTOR * 3) ]

class MW2_View_Y(Structure):
    _fields_ = [ ("Recoil", VECTOR),        # 0x0000
                 ("_p00", c_char * 24),
                 ("viewAngles", VECTOR),
                 ("_p01", c_char * 16),
                 ("AngleY", c_float),
                 ("AngleX", c_float) ]

class STR16(Structure):
    _fields_ = [ ("str", c_char * 16)]
    
class STR64(Structure):
    _fields_ = [ ("str", c_char * 64)]

class MW2_ClientInfo_T(Structure):
    _fields_= [ ("_p00", c_char * 12),
                ("name", STR16),
                ("team", c_uint),
                ("team2", c_uint),
                ("_p01", c_char * 8),
                ("perk", c_uint),
                ("_p02", c_char * 16),
                ("BodyModel", STR64),
                ("HeadModel", STR64),
                ("WeaponModel", STR64),
                ("WeaponModel2", STR64),
                ("WeaponExplosive", STR64),
                ("_p03", c_char * 552),
                ("pose", c_uint),
                ("_p04", c_char * 96),
                ("pose2", c_uint),
                ("_p05", c_char * 284),
               ]

class MW2_Entity_T(Structure):
    _fields_= [ ("_p00", c_ushort),     # 0x00
                ("valid", c_ushort),    # 0x02
                ("_p01", c_char * 20),  # 0x04
                ("pos", VECTOR),        # 0x18
                ("fPitch", c_float),    # 0x24
                ("fYaw", c_float),      # 0x28
                ("fRoll", c_float),     # 0x2C
                ("_p02", c_char * 60),  # 0x30
                ("pose", c_uint),       # 0x6C
                ("_p03", c_char * 12),  # 0x70
                ("pX", c_float),        # 0x7C
                ("pY", c_float),        # 0x80
                ("pZ", c_float),        # 0x84
                ("_p04", c_char * 84),  # 0x88
                ("clientNum", c_int),   # 0xDC
                ("type", c_int),        # 0xE0
                ("PlayerPose", c_ubyte),# 0xE4
                ("Shooting", c_ubyte),  # 0xE5
                ("Zoomed", c_ubyte),    # 0xE6
                ("_p05", c_ubyte),      # 0xE7
                ("_p06", c_char * 192), # 0xE8
                ("WeaponNum", c_short), # 0x1A8
                ("_p07", c_char * 50),  # 0x1AA
                ("alive", c_int),       # 0x1DC
                ("_p08", c_char * 36),  # 0x1E0
                ]                       # 0x204

class MW2_ClientInfo(Structure):
    _fields_ = [ ("arr", MW2_ClientInfo_T * PLAYERMAX) ]

class MW2_Entity(Structure):
    _fields_ = [ ("arr", MW2_Entity_T * ENTITIESMAX) ]

# high level Player object

class Player(object):
    __slots__ = ( 'valid', 'pos', 'pitch', 'yaw', 'roll', 'client_num', 'type', 'pose', 'shooting', 'zoomed',
                  'weapon_num', 'alive', 'enemy', 'name', 'team', 'perk', 'color_esp', 'color_map')
   
    def __init__(self):
        self.valid = 0
        self.pos = None
        self.pitch = 0
        self.yaw = 0
        self.roll = 0
        self.client_num = 0
        self.type = 0
        self.pose = 0
        self.shooting = 0
        self.zoomed = 0
        self.weapon_num = 0
        self.alive = 0
        self.enemy = False

        self.name = ""
        self.team = 0
        self.perk = 0
        
        self.color_esp = 0
        self.color_map = 0

    def set_values(self, mw2_entity, mw2_clientinfo):
        self.valid = mw2_entity.valid
        self.pos = mw2_entity.pos
        self.pitch = mw2_entity.fPitch
        self.yaw = mw2_entity.fYaw
        self.roll = mw2_entity.fRoll
        self.client_num = mw2_entity.clientNum
        self.type = mw2_entity.type
        self.pose = mw2_entity.PlayerPose
        self.shooting = mw2_entity.Shooting
        self.zoomed = mw2_entity.Zoomed
        self.weapon_num = mw2_entity.WeaponNum
        self.alive = mw2_entity.alive
        self.enemy = False
        
        p_str = cast(pointer(mw2_clientinfo.name), c_char_p)
        self.name = p_str.value
        self.team = mw2_clientinfo.team
        self.perk = mw2_clientinfo.perk
