from Config import * #@UnusedWildImport
from utils import draw_spot, mouse_move
from Keys import keys
from structs import ET_PLAYER, FLAGS_CROUCHED, FLAGS_PRONE, VECTOR, ALIVE_FLAG
from math import sqrt

INFINITY = 1e100000         # trick to backport float('inf') to python 2.5

class Bot(object):
    
    def __init__(self, env):
        self.env = env
        self.player_locked = None               # -1 means unlocked
        self.player_locked_ticks = 0            # tick count when player lock started
        self.mouse_move_x = 0
        self.mouse_move_y = 0
        self.last_mouse_move = 0
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        esp = self.env.esp
        weapon_names = self.env.weapon_names
        self.mouse_move_x = 0
        self.mouse_move_y = 0
        if not read_game.is_in_game:
            self.last_mouse_move = 0
            return
        key_tubebot = False
        hop = False             # is True when you are locked on a player but he was killed (by you or other)
        
        key_bot = keys["KEY_BOT"] and keys["KEY_AIMBOT_ACTIVE"]
        if self.is_sniper():
            if (self.env.read_game.my_player.zoomed):
                key_bot |= keys["KEY_SNIPER_BOT"] and keys["KEY_AIMBOT_ACTIVE"]
        # ammo left?
#        if weapon_names.get_current_weapon() < 1642:            # 1642 = C4 charge
#            key_bot = key_bot and weapon_names.get_ammo(weapon_names.get_current_weapon()) > 0
        
        if self.is_tube_active() and key_bot:
            key_tubebot = keys["KEY_TUBEBOT"]

        key_knifebot = keys["KEY_KNIFEBOT"] and keys["KEY_KNIFEBOT_ACTIVE"]
        # we limit knifebot to tomahawk right now
        key_knifebot = key_knifebot and weapon_names.get_weapon_model(weapon_names.get_frag_grenade()) == "hatchet_mp"
        # is there ammo left for knifebot?
        key_knifebot = key_knifebot and weapon_names.get_ammo(weapon_names.get_frag_grenade()) > 0
        
        if self.player_locked and not (self.player_locked.alive & ALIVE_FLAG):
            self.player_locked = None           # if player dead, cancel locked tracking
            hop = True                          # was killed so do HOP tracking
        
        if self.player_locked and not key_bot and not key_knifebot and not key_tubebot:
            self.player_locked = None           # all tracking keys released
            
        bot_range = read_game.player[:]            # iterate through all players
        # now add tracked entities
        bot_range.extend(self.env.tracker.get_aimbot_tracked_entities())

        if self.player_locked:
            bot_range = [ self.player_locked ]  # only 1 item
        
        angle_dist = INFINITY                   # current distance to the center
        aimed_player = None                     # currently aimed player
        angle = [0, 0]
        
        BOT_MAX_PIX_TO_CENTER = int(BOT_MAX_TO_CENTER * read_game.resolution_x)     # calculated from resolution
        BOT_HOP_MAX_PIX_TO_CENTER = int(BOT_HOP_MIN_TO_CENTER * read_game.resolution_x)     # calculated from resolution
        #Aimbot
        for p in bot_range:                                
            if p.aimbot and p != read_game.my_player and p.valid and p.alive & ALIVE_FLAG and p.enemy:
                aim_target = p.pos + (p.newpos - p.oldpos).scalar_mul(BOT_MOTION_COMPENSATE)
                if p.type == ET_PLAYER:
                    if key_tubebot:
                        aim_target.z += BOT_TUBE_Z
                    elif key_knifebot:
                        aim_target.z += BOT_KNIFE_Z - 30    # 40: compensate for hand being lower than eye when throwing
                    else:
                        if p.pose & FLAGS_CROUCHED:
                            aim_target.z += BOT_CROUCHED_Z
                        elif p.pose & FLAGS_PRONE:
                            aim_target.z += BOT_PRONE_Z
                        else:
                            aim_target.z += BOT_STAND_Z
                    box = esp.calc_player_rect(p)                   # get the bounding box of player
                else:
                    aim_target.z += 20          # XXX for rcxd and dogs // to be refined
                    box = esp.calc_tracked_rect(p)
                    
                spot = read_game.world_to_screen(aim_target)    # calculate the spot location on screen
                player_dist = self.sq(read_game.my_pos.x - p.pos.x, read_game.my_pos.y - p.pos.y) + .1  # calculate player distance
                if spot and box and box.left < read_game.screen_center_x and box.right > read_game.screen_center_x and box.top < read_game.screen_center_y and box.bottom > read_game.screen_center_y:
                    # Crosshair in bounding box
                    cur_angle_dist = -1.0 / player_dist     # here cur_angle_dist will be negative
                    if cur_angle_dist < angle_dist:
                        # select this player
                        angle_dist = cur_angle_dist
                        angle = [spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y]
                        aimed_player = p
                elif spot:
                    cur_angle_dist = self.sq(spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y)
                    # square of the distance of the spot to the center of the screen
                    if hop:                 # if hopping from one player to another, reduce the screen area to scan
                        bot_max_pix = BOT_HOP_MAX_PIX_TO_CENTER
                    else:
                        bot_max_pix = BOT_MAX_PIX_TO_CENTER
                    if cur_angle_dist < bot_max_pix * bot_max_pix:      # not too far from center
                        cur_angle_dist = cur_angle_dist * player_dist
                        if cur_angle_dist < angle_dist:
                            # select this player
                            angle_dist = cur_angle_dist
                            angle = [spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y]
                            aimed_player = p
            
        # end for
        if self.player_locked and not key_tubebot and not key_knifebot and aimed_player is None:
            self.player_locked = None           # if player locked is off range, and not tube/knife, we release lock
            
        if angle_dist != INFINITY and self.player_locked is None and (key_tubebot or key_knifebot or key_bot):
            # just starting a player lock sequence
            self.player_locked = aimed_player               # lock on player
            self.player_locked_ticks = self.env.ticks       # take the timestamp of the lock

        if angle_dist != INFINITY and (keys["KEY_AIMBOT_ACTIVE"] or keys["KEY_TUBEBOT_ACTIVE"] or keys["KEY_KNIFEBOT_ACTIVE"]) and keys["KEY_BOT_DRAW_SPOT"]:
            # draw white spot on the targeted player
            draw_spot(frame.line, read_game.screen_center_x + angle[0], read_game.screen_center_y + angle[1], BOT_FRAME_COLOR)

        if self.player_locked:
            #print "time=%i, alive=%2x, alive2=%2x, moving=%2x, poser=%2x" % (self.env.read_game.game_time, self.player_locked.alive, self.player_locked.entity.isalive2, self.player_locked.entity.movingState, self.player_locked.client_info.pose)
            if key_tubebot or key_knifebot:
                aim = self.player_locked.pos
                velocity = TUBE_VEL
                if key_knifebot:
                    velocity = KNIFE_VEL
                    aim.z += BOT_KNIFE_Z             # middle of body
                slope = self.find_slope(aim, read_game.my_pos, velocity)
                if not slope is None:
                    aim.z = read_game.my_pos.z + slope * (aim - read_game.my_pos).length()
                    spot_coord = read_game.world_to_screen(aim)
                    if spot_coord:
                        angle[0] = spot_coord.x - read_game.screen_center_x
                        angle[1] = spot_coord.y - read_game.screen_center_y
                        mouse_move(angle[0] / 1.2, angle[1] / 1.2, read_game.mouse_center_x, read_game.mouse_center_y, read_game.sensitivity)
                else:
                    self.player_locked = None
            elif key_bot:
                # aimbot is triggered through maintained right click or END key
    
                # aiming is accelerated in time to better target moving players, otherwise you're
                # always aiming behind the player
                # dividing by 7 gives a rather natural while quick aiming
                aim_speed = BOT_SPEED_1
                if self.env.ticks - self.player_locked_ticks > BOT_SPEED_TICK_1:
                    aim_speed = BOT_SPEED_2
                if self.env.ticks - self.player_locked_ticks > BOT_SPEED_TICK_2:
                    aim_speed = BOT_SPEED_3
                self.mouse_move(angle[0] / aim_speed, angle[1] / aim_speed, read_game.mouse_center_x, read_game.mouse_center_y, read_game.sensitivity)
            else:
                self.player_locked = None
        
        # debug mode calibration - aiming at (0,0,0) point
        if CALIBRATING:
            origin = VECTOR(640, 395, 0)
            spot_coord = read_game.world_to_screen(origin)
            if spot_coord:
                draw_spot(frame.line, spot_coord.x, spot_coord.y, 0x7FFFFFFF)
            if key_tubebot or key_knifebot:
                velocity = TUBE_VEL
                if key_knifebot:
                    velocity = KNIFE_VEL
                slope = self.find_slope(origin, read_game.my_pos, velocity)
                if not slope is None:
                    origin.z = read_game.my_pos.z + slope * (origin - read_game.my_pos).length()
                    spot_coord = read_game.world_to_screen(origin)
                    if spot_coord:
                        angle[0] = spot_coord.x - read_game.screen_center_x
                        angle[1] = spot_coord.y - read_game.screen_center_y
                        print "slope = %.3f, angle = %.3f, %.3f" % (slope, angle[0], angle[1])
                        self.mouse_move(angle[0], angle[1], read_game.mouse_center_x, read_game.mouse_center_y, read_game.sensitivity)
            elif key_bot:
                if spot_coord:
                    angle[0] = spot_coord.x - read_game.screen_center_x
                    angle[1] = spot_coord.y - read_game.screen_center_y
                    print "time = %i   angle = %.3f, %.3f" % (read_game.game_time, angle[0], angle[1])
                    self.mouse_move(angle[0], angle[1], read_game.mouse_center_x, read_game.mouse_center_y, read_game.sensitivity)

    @staticmethod
    def find_slope(target, player, vel):
        # calculate the slope (or tan(angle)) based on the trajectory of grenade
        # see: http://en.wikipedia.org/wiki/Trajectory_of_a_projectile#Angle_.CE.B8_required_to_hit_coordinate_.28x.2Cy.29
        sq_vel = vel * vel
        dz = target.z - player.z
        range = (target - player).length()      # length of vector from player to target
        discr = sq_vel*sq_vel - GRAV*GRAV*range*range - 2*GRAV*dz*sq_vel
        if discr < 0: return None
        if keys["KEY_INDIRECT_BOT"]:
            traj_slope = ( (sq_vel + sqrt(discr))/(GRAV*range +.000001) )       # indirect
        else:
            traj_slope = ( (sq_vel - sqrt(discr))/(GRAV*range +.000001) )       # direct
        if traj_slope < 10 and traj_slope > -10:                                # ~85 degrees up or down max
            return traj_slope
        else:
            return None

    def mouse_move(self, delta_x, delta_y, center_x, center_y, sensitivity):
        cur_time = self.env.read_game.game_time
        if cur_time != self.last_mouse_move:                # check whether time changed since last mpuse_move
            self.last_mouse_move = cur_time
            (mouse_move_x, mouse_move_y) = mouse_move(delta_x, delta_y, center_x, center_y, sensitivity)
            self.mouse_move_x = mouse_move_x
            self.mouse_move_y = mouse_move_y

    @staticmethod
    def sq(x, y):
        return x*x + y*y
                        
    def is_tube_active(self):
        wn = self.env.weapon_names
        return wn.is_grenade_launcher(wn.get_current_weapon())
    
    def is_sniper(self):
        wn = self.env.weapon_names
        return wn.is_sniper_rifle(wn.get_current_weapon())
