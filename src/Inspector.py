from utils import draw_string_center
from Config import KEY_INSPECTOR
from Keys import keys
from utils import dump
# this module allows to inspect entities near the center crosshair


class Inspector(object):
    
    def __init__(self, env):
        self.env = env
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        #if not read_game.is_in_game or not keys["KEY_INSPECTOR"]: return
        if keys["KEY_INSPECTOR"]: 
            for e in read_game.mw2_entity.arr:
                spot = read_game.world_to_screen(e.pos)
                if spot:
                    cur_angle_dist = self.sq(spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y)
                    if cur_angle_dist < 50 * 50:      # not too far from center
                        s = "[typ=%i, %i, %i]" % (e.type, e.clientNum, e.WeaponNum) 
                        draw_string_center(frame.font, spot.x, spot.y, 0xFFFFFFFF, s)
                        print s
        
        if keys["KEY_INSPECT_POS"]:                 # print my player's position
            pos = read_game.mw2_mypos
            print "pos= (%.2f, %.2f, %.2f)" % (pos.x, pos.y, pos.z)
            ang = read_game.view_angles
            print "angles= (%.2f, %.2f, %.2f)" % (ang.x, ang.y, ang.z)
        
        if keys["KEY_INSPECT_DUMP"]:                # dump some memory structures
            print "refdef"
            dump(read_game.mw2_refdef)
            print "viewy"
            dump(read_game.mw2_viewy)

    @staticmethod
    def sq(x, y):
        return x*x + y*y