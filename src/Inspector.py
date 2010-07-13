from utils import draw_string_center
from Config import KEY_INSPECTOR
from Keys import keys
from utils import dump_obj
from ctypes import Structure, c_char
from structs import ET_EXPLOSIVE, ENTITIESMAX, PLAYERMAX
# this module allows to inspect entities near the center crosshair

class dumped(Structure):
    _fields_ = [("val", c_char * 1024)]

class Inspector(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        #if not read_game.is_in_game or not keys["KEY_INSPECTOR"]: return
        if keys["KEY_INSPECTOR"]: 
            for idx in range(ENTITIESMAX):
                e = read_game.mw2_entity.arr[idx]
                spot = read_game.world_to_screen(e.pos)
                if spot:
                    cur_angle_dist = self.sq(spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y)
                    if cur_angle_dist < 50 * 50:      # not too far from center
                        s = "[idx=%i, typ=%i, weap=%i]" % (idx, e.type, e.WeaponNum) 
                        draw_string_center(frame.font, spot.x, spot.y, 0xFFFFFFFF, s)
                        print s
                        print dump_obj(e)
                        #=======================================================
                        # if e.type == ET_EXPLOSIVE:
                        #    print "dump explo"
                        #    print dump_obj(e)
                        #=======================================================
        
        if keys["KEY_INSPECT_POS"]:                 # print my player's position
            pos = read_game.mw2_mypos
            print "pos= (%.2f, %.2f, %.2f)" % (pos.x, pos.y, pos.z)
            ang = read_game.view_angles
            print "angles= (%.2f, %.2f, %.2f)" % (ang.x, ang.y, ang.z)
        
        if keys["KEY_INSPECT_DUMP"]:                # dump some memory structures
            #mem = dumped()
            #read_game._RPM(0x6727F13, mem)
            #read_game._RPM(0x6727F10, mem)
            #print dump_obj(mem)
            #read_game._RPM(0x64DA350, mem)
            for i in range(8):
                print "player #%i" % i
                print dump_obj(read_game.mw2_entity.arr[i])
                print "client info"
                print dump_obj(read_game.mw2_clientinfo.arr[i])
            #del mem
            #===================================================================
            # print "refdef"
            # print dump_obj(read_game.mw2_refdef)
            # print "viewy"
            # print dump_obj(read_game.mw2_viewy)
            #===================================================================
        
        if False and read_game.is_in_game:
            print "time=%8i, pos2=%.1f %.1f %.1f, pos3=%.1f %.1f %.1f" % (read_game.game_time,
                                                                         read_game.my_player.pos2.x,
                                                                         read_game.my_player.pos2.y,
                                                                         read_game.my_player.pos2.z,
                                                                         read_game.my_player.pos3.x,
                                                                         read_game.my_player.pos3.y,
                                                                         read_game.my_player.pos3.z,
                                                                         )
            
        if False and read_game.is_in_game:
            print "time=%8i, motion=%.1f %.1f %.1f, abs=%.1f" % (read_game.game_time,
                                                                         read_game.my_player.motion.x,
                                                                         read_game.my_player.motion.y,
                                                                         read_game.my_player.motion.z,
                                                                         read_game.my_player.motion.length()
                                                                         )
        if False:
            for e in read_game.mw2_entity.arr:
                if e.type == ET_EXPLOSIVE and e.alive & 0x0001:
                    print "time=%8i, pos=%.1f %.1f %.1f" % (read_game.game_time,
                                                                                 e.pos.x,
                                                                                 e.pos.y,
                                                                                 e.pos.z,
                                                                                 )
        

    @staticmethod
    def sq(x, y):
        return x*x + y*y