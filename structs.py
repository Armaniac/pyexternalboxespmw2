from ctypes import * #@UnusedWildImport
#from UserList import UserList
import math

PLAYERMAX = 32            # number of players to loop in
ENTITIESMAX = 1024        # total number of entities present XXX

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
ET_ACTOR            = 17
ET_ACTOR_SPAWNER    = 18
ET_ACTOR_CORPSE     = 19
ET_STREAMER_HINT    = 20

ALIVE_FLAG          = 0x02
ALIVE_FIRING        = 0x04

FLAGS_CROUCHED      = 0x000004
FLAGS_PRONE         = 0x000008

PERK_STEALTH        = 0x40000           # Hmmm doesn't seem to work XXX

TEAM_FREE           = 0
TEAM_ALLIES         = 1
TEAM_AXIS           = 2
TEAM_SPECTATOR      = 3
TEAM_DEATHMATCH     = 4
TEAM_NUM_TEAMS      = 5

# memory structures
class VECTOR(Structure):
    _fields_ = [ ("x", c_float),
                 ("y", c_float),
                 ("z", c_float) ]
    
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    def dotProduct(self, dot):
        return self.x*dot.x + self.y*dot.y + self.z*dot.z;
    def scalar_mul(self, multiplier):
        return VECTOR(self.x * multiplier, self.y * multiplier, self.z * multiplier)
    def __add__(self, other):
        return VECTOR(self.x+other.x, self.y+other.y, self.z+other.z)
    def __sub__(self, other):
        return VECTOR(self.x-other.x, self.y-other.y, self.z-other.z)

class COORD(Structure):
    _fields_ = [ ("x", c_float),
                 ("y", c_float) ]

class RECT(Structure):
    _fields_ = [ ("left", c_int),
                 ("top", c_int),
                 ("right", c_int),
                 ("bottom", c_int) ]

class POINT(Structure):
    _fields_ = [ ("x", c_int),
                 ("y", c_int) ]

class MSG(Structure):
    _fields_ = [('hwnd', c_int),
                ('message', c_uint),
                ('wParam', c_int),
                ('lParam', c_int),
                ('time', c_int),
                ('pt', POINT)]

class COD7_RefDef(Structure):
    _fields_ = [ 
                 ("viewAngles", VECTOR),    # 0x00
                 ("_buf", c_char * 0x14C),  
                 ("x", c_int),              # 0x00
                 ("y", c_int),              # 0x04
                 ("width", c_int),          # 0x08
                 ("height", c_int),         # 0x0C
                 ("fov_x", c_float),        # 0x10
                 ("fov_y", c_float),        # 0x14
                 ("totalfov", c_float),     # 0x18
                 ("viewOrg", VECTOR),       # 0x1C
                 ("other", c_int),      # 0x28
                 ("viewAxis", VECTOR * 3),  # 0x2C
                 ]

class COD7_CG_T(Structure):
    _fields_ = [ ("clientNum", c_int),          # 0x00
                 ("_p00", c_char * 32),         # 0x04
                 ("time", c_int),               # 0x24
                 ("snap", c_int),               # 0x28
                 ("nextSnap", c_int),           # 0x2C
                 ("_p01", c_char * 84),         # 0x30
                 ("ping", c_int),               # 0x84
                 ("_p02", c_char * 44),         # 0x88
                 ("lerpOrigin", VECTOR),        # 0xB4
                 ("newOrigin", VECTOR),         # 0xC0
                 ("_p03", c_char * 16),         # 0xCC
                 ("zoomTime", c_int),           # 0xDC
                 ("_p04", c_char * 244),        # 0xE0
                 ("weapon", c_int),             # 0x1D4
                 ("_p05", c_char * 16),         # 0x1E4
                 ("state", c_int),              # 0x1E8    1:3:4:Switching Weapon; 6:Shooting; 12:Reload Start; 10:Reloading; 14:Reload End; 27:Sprint Start; 28:Sprinting; 29:Sprint End
                 ("isClimbing", c_int),         # 0x1EC    4:Climbing
                 ("_p06", c_char * 8),          # 0x1F0
                 ("isZoomed", c_float),         # 0x1F8
                 ("_p07", c_char * 20),         # 0x1FC
                 ("viewAngleY", c_float),       # 0x210
                 ("viewAngleX", c_float),       # 0x214
                 ("_p09", c_char * 564),        # 0x218
                 ("ammo_prim", c_int),          # 0x44C
                 ("_p19", c_char * 4),          # 0x450
                 ("ammo_second", c_int),        # 0x454
                 ("_p29", c_char * 4),          # 0x458
                 ("ammo_nade", c_int),          # 0x45C
                 ("_p39", c_char * 4),          # 0x460
                 ("ammo_smoke", c_int),         # 0x464
                 ("_p49", c_char * 12),         # 0x468
                 ("killstreak", c_int),         # 0x474
                 ("_p59", c_char * 12),         # 0x478
                 ("ammo_right", c_int),         # 0x484
                 ("_p69", c_char * 4),          # 0x488
                 ("ammo_left", c_int),          # 0x48C
                 ]                              # 0x490

class COD7_SNAPSHOT_T(Structure):
    _fields_ = [ ("snapFlags", c_int),          # 0x00
                 ("ping", c_int),               # 0x04
                 ("serverTime", c_int),         # 0x08
                 ("_p00", c_char * 16),         # 0x0C
                 ("isReloading", c_int),        # 0x1C
                 ("_p01", c_char * 20),         # 0x20
                 ("viewOrg", VECTOR),           # 0x34
                 ("deltaX", c_float),           # 0x40
                 ("deltaY", c_float),           # 0x44
#                 ("_p02", c_char * 168),        # 0x48
#                 ("stance", c_int),             # 0xF0 0:Standing; 4:Crouching; 8:Prone;
#                 ("_p03", c_char * 264),        # 0xF4
                ]

class STR16(Structure):
    _fields_ = [ ("str", c_char * 16)]
class STR32(Structure):
    _fields_ = [ ("str", c_char * 32)]
    
class STR64(Structure):
    _fields_ = [ ("str", c_char * 64)]

class COD7_CGS_T(Structure):
    _fields_ = [ ("_p00", c_char * 32),         # 0x00
                 ("gamemode", c_char * 4),      # 0x20
                 ("_p01", c_char * 28),         # 0x24
                 ("server", STR16),             # 0x40
                 ("_p02", c_char * 244),        # 0x50
                 ("map", c_char * 32),          # 0x144
                ]
    
class COD7_ClientInfo_T(Structure):
    _fields_= [ ("infoValid", c_int),   # 0x000
                ("infoValid2", c_int),  # 0x004
                ("index", c_int),       # 0x008
                ("name", STR32),        # 0x00C
                ("team", c_int),        # 0x02C
                ("team2", c_int),       # 0x030
                ("_p02", c_char * 4),   # 0x034
                ("rank", c_int),        # 0x038
                ("_p03", c_char * 52),  # 0x03C
                ("kills", c_int),       # 0x070
                ("assist", c_int),      # 0x074
                ("deaths", c_int),      # 0x078
                ("_p09", c_char * 976), # 0x07C
                ("anglex", c_float),    # 0x44C
                ("angley", c_float),    # 0x450
                ("_p04", c_char * 168), # 0x454
                ("pose", c_int),        # 0x4FC
                ("_p05", c_char * 4),   # 0x500
                ("isshooting", c_int),  # 0x504
                ("iszoomed", c_int),    # 0x508
                ("_p06", c_char * 44),  # 0x50C
                ("weapon", c_int),      # 0x538
                ("_p07", c_char * 140), # 0x53C
               ]                        # 0x5C8

class COD7_Entity_T(Structure):
    _fields_= [ ("_p00", c_char * 48),      # 0x000
                ("pos", VECTOR),            # 0x030
                ("anglex", c_float),        # 0x03C
                ("angley", c_float),        # 0x040
                ("anglez", c_float),        # 0x044
                ("_p01", c_char * 320),     # 0x048
                ("newpos", VECTOR),         # 0x188
                ("_p02", c_char * 24),      # 0x194
                ("angle2", VECTOR),         # 0x1AC
                ("_p12", c_char * 48),      # 0x1B8
                ("clientnum", c_int),       # 0x1E9
                ("pose", c_int),            # 0x1EC 0:Not Zoomed 0x40000 stealth perk?
                ("_p22", c_char * 16),      # 0x1F0
                ("oldpos", VECTOR),         # 0x200
                ("_p03", c_char * 24),      # 0x20C
                ("oldangle", VECTOR),       # 0x224
                ("_p13", c_char * 20),      # 0x230
                ("movingState", c_int),     # 0x244 1:Standing Still; 3:Prone or ADS Moving; 4:Walking; 7:Running
                ("weaponId", c_int),        # 0x248
                ("_p23", c_char * 90),      # 0x24C    
                ("type", c_short),          # 0x2A6
                ("_p04", c_char * 10),      # 0x2A8
                ("weapon", c_short),        # 0x2B2
                ("_p14", c_char * 112),     # 0x2B4
                ("alive", c_ubyte),         # 0x324
                ("isalive2", c_ubyte),      # 0x325
                ("_p05", c_char * 2),       # 0x326
                ]                           # 0x328

class COD7_ClientInfo(Structure):
    _fields_ = [ ("arr", COD7_ClientInfo_T * PLAYERMAX) ]

class COD7_Entity(Structure):
    _fields_ = [ ("arr", COD7_Entity_T * ENTITIESMAX) ]

class COD7_WeaponDesc_T(Structure):
    _fields_ = [ ("model", c_int),          # 0x00
                 ("i1", c_int),             # 0x04
                 ("i2", c_int),             # 0x08
                 ("name_addr", c_int),      # 0x0C
                 ("_p99", c_char * 0xD4),   # 0x10
                 ]                          # 0xE4

class COD7_WeaponDesc(Structure):
    _fields_ = [ ("arr", c_int * 2048)]

class STR256(Structure):
    _fields_ = [ ("str", c_byte * 256)]
# high level Player object

class Player(object):
   
    def __init__(self):
        self.valid = 0
        self.pos = None
        self.newpos = None
        self.oldpos = None
        self.prev_pos = None
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
        self.motion = VECTOR(0, 0, 0)               # motion vector of the player, in game units per second
        
        self.entity = None
        self.client_info = None

    def set_values(self, cod7_entity, cod7_clientinfo):
        self.entity = cod7_entity
        self.client_info = cod7_clientinfo
        #self.valid = cod7_entity.valid
        self.valid = True
        self.prev_pos = self.pos
        self.pos = cod7_entity.pos
        self.newpos = cod7_entity.newpos
        self.oldpos = cod7_entity.oldpos
        self.pitch = cod7_entity.anglex
        self.yaw = cod7_entity.angley
        #self.roll = cod7_entity.fRoll
        #self.client_num = cod7_entity.clientNum
        self.type = cod7_entity.type
        #self.shooting = cod7_entity.Shooting
        #self.zoomed = cod7_entity.Zoomed
        self.weapon_num = cod7_entity.weapon
        self.alive = cod7_entity.alive
        
        p_str = cast(pointer(cod7_clientinfo.name), c_char_p)
        self.name = p_str.value
        self.team = cod7_clientinfo.team
        self.pose = cod7_entity.pose
        self.perk = cod7_entity.pose

class EntityTracker(object):
    __slots__ = ( 'idx', 'startoflife', 'endoflife', 'pos', 'yaw', 'type', 'alive', 'weapon_num', 'model_name', 'planter')
    
    def __init__(self, idx):
        self.idx = idx                      # index of entity object
        self.startoflife = -1               # time_code when the entity was first tracked
        self.endoflife = -1                 # time_code when the object will not exist anymore
        self.pos = VECTOR()                 # position
        self.yaw = 0
        self.type = 0                       # type of object (as in entity)
        self.alive = 0                      # alive attribute (as in entity)
        self.weapon_num = 0                 # weaponnum (as in entity)
        self.model_name = ""                # model name
        self.planter = None                 # player who planted the explosive
    
    def set_values(self, cod7_entity):
        self.pos = cod7_entity.pos
        self.yaw = cod7_entity.angley
        self.type = cod7_entity.type
        self.alive = cod7_entity.alive
        self.weapon_num = cod7_entity.weapon

if __name__ == "__main__":
    print "Sizeof COD7_Entity_T is 0x%x, should be 0x328" % sizeof(COD7_Entity_T)
    print "Sizeof COD7_ClientInfo_T is 0x%x, should be 0x5C8" % sizeof(COD7_ClientInfo_T)