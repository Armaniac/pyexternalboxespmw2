from utils import draw_string_center
from Keys import keys
from utils import dump_obj, mouse_move
from ctypes import Structure, c_char
from structs import ET_EXPLOSIVE, ENTITIESMAX, PLAYERMAX, VECTOR
# this module allows to inspect entities near the center crosshair

class dumped(Structure):
    _fields_ = [("val", c_char * 1024)]

class Inspector(object):
    
    def __init__(self, env):
        self.env = env
    
    def move_sequence(self):                 # coroutine
        yield
        read_game = self.env.read_game
        old_va = read_game.view_angles
        for i in range(15): #@UnusedVariable
            va = read_game.view_angles
            print "va = %.2f %.2f %.2f" % (va.x, va.y, va.z)
            print "dd = %.2f %.2f %.2f" % (va.x - old_va.x, va.y - old_va.y, va.z - old_va.z)
            print "moving 10 pix right, fov_x=%.2f fov_y=%.2f sensitivity = %.1f" % (read_game.fov_x, read_game.fov_y, read_game.sensitivity)
            old_va = VECTOR(va.x, va.y, va.z)
            mouse_move(10.0, 0.0, read_game.mouse_center_x, read_game.mouse_center_y, read_game.sensitivity)
            yield
            yield
            yield
            yield
            yield
            yield
        for i in range(10): #@UnusedVariable
            va = read_game.view_angles
            print "va = %.2f %.2f %.2f" % (va.x, va.y, va.z)
            print "dd = %.2f %.2f %.2f" % (va.x - old_va.x, va.y - old_va.y, va.z - old_va.z)
            print "moving 10 pix down, sensitivity = %.1f" % read_game.sensitivity
            old_va = VECTOR(va.x, va.y, va.z)
            mouse_move(0.0, 10.0, read_game.mouse_center_x, read_game.mouse_center_y, read_game.sensitivity)
            yield
            yield
            yield
            yield
            yield
            yield
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        #if not read_game.is_in_game or not keys["KEY_INSPECTOR"]: return
        if keys["KEY_INSPECTOR"]: 
            for i in range(PLAYERMAX):
                print "Player #%i: %s" % (i, read_game.player[i].name)
            for idx in range(ENTITIESMAX):
                e = read_game.mw2_entity.arr[idx]
                spot = read_game.world_to_screen(e.pos)
                if spot:
                    cur_angle_dist = self.sq(spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y)
                    if cur_angle_dist < 50 * 50:      # not too far from center
                        s = "[idx=%i(%x), typ=%i, weap=%i]" % (idx, idx, e.type, e.WeaponNum)
                        draw_string_center(frame.font, spot.x, spot.y, 0xFFFFFFFF, s)
                        print s
                        print dump_obj(e)
#                        if e.owner_scr1 >= 0 and e.owner_scr1 < 2047:
#                            ee = read_game.mw2_entity.arr[e.owner_scr1]
#                            print "[idx=%i(%x), typ=%i, weap=%i]" % (e.owner_scr1, e.owner_scr1, ee.type, ee.WeaponNum)
#                            print dump_obj(ee)
#                        if e.owner_scr2 >= 0 and e.owner_scr2 < 2047:
#                            ee = read_game.mw2_entity.arr[e.owner_scr2]
#                            print "[idx=%i(%x), typ=%i, weap=%i]" % (e.owner_scr2, e.owner_scr2, ee.type, ee.WeaponNum)
#                            print dump_obj(ee)
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
        
        if keys["KEY_INSPECT_DUMP_PLAYERS"]:
            for i in range(PLAYERMAX):
                print "Player #%i: %s" % (i, read_game.player[i].name)
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
        if False and read_game.is_in_game:
            print "kills=%i, deaths=%i" % (read_game.kills, read_game.deaths)
                                          
        if False and read_game.is_in_game:
            print "weapon=%i" % read_game.my_player.weapon_num
            
        if keys["KEY_INSPECT_MOVE_MOUSE"]:
            self.env.sched.new(self.move_sequence())
        

    @staticmethod
    def sq(x, y):
        return x*x + y*y