from Config import *
from utils import draw_spot, mouse_move
from Keys import keys
from structs import ET_PLAYER, FLAGS_CROUCHED, FLAGS_PRONE, VECTOR



class Bot(object):
    
    def __init__(self, env):
        self.env = env
        self.player_locked = None               # -1 means unlocked
        self.player_locked_ticks = 0            # tick count when player lock started
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        if not read_game.is_in_game: return
        key_bot = keys["KEY_BOT"] and keys["KEY_AIMBOT_ACTIVE"]
        key_tubebot = keys["KEY_TUBEBOT"] and keys["KEY_TUBEBOT_ACTIVE"]
        key_knifebot = keys["KEY_KNIFEBOT"] and keys["KEY_KNIFEBOT_ACTIVE"]
        
        if self.player_locked and not (self.player_locked.alive & 0x0001):
            self.player_locked = None           # if player dead, cancel locked tracking
        
        if self.player_locked and not key_bot and not key_knifebot and not key_tubebot:
            self.player_locked = None           # all tracking keys released
            
        bot_range = read_game.player            # iterate through all players
        if self.player_locked:
            bot_range = [ self.player_locked ]  # only 1 item
        
        angle_dist = -1                         # current distance to the center
        aimed_player = None                     # currently aimed player
        angle = [0, 0]
        for p in bot_range:
            if p != read_game.my_player and p.type == ET_PLAYER and p.valid and p.alive & 0x0001 and p.enemy:
                aim_target = p.pos
                if key_tubebot:
                    aim_target.z += BOT_TUBE_Z
                elif key_knifebot:
                    aim_target.z += BOT_KNIFE_Z
                else:
                    if p.pose & FLAGS_CROUCHED:
                        aim_target.z += BOT_CROUCHED_Z
                    elif p.pose & FLAGS_PRONE:
                        aim_target.z += BOT_PRONE_Z
                    else:
                        aim_target.z += BOT_STAND_Z
                
                spot = read_game.world_to_screen(aim_target)
                if spot:
                    cur_angle_dist = self.sq(spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y)
                    # square of the distance of the spot to the center of the screen
                    if cur_angle_dist < BOT_MIN_PIX_TO_CENTER * BOT_MIN_PIX_TO_CENTER:      # not too far from center
                        if angle_dist < 0 or cur_angle_dist < angle_dist:
                            # select this player
                            angle_dist = cur_angle_dist
                            angle = [spot.x - read_game.screen_center_x, spot.y - read_game.screen_center_y]
                            aimed_player = p
        # end for
        if self.player_locked and not key_tubebot and not key_knifebot and aimed_player is None:
            self.player_locked = None           # if player locked is off range, and not tube/knife, we release lock
            
        if angle_dist > 0 and self.player_locked is None and (key_tubebot or key_knifebot or key_bot):
            # just starting a player lock sequence
            self.player_locked = aimed_player               # lock on player
            self.player_locked_ticks = self.env.ticks       # take the timestamp of the lock

        if angle_dist > 0 and (keys["KEY_AIMBOT_ACTIVE"] or keys["KEY_TUBEBOT_ACTIVE"] or keys["KEY_KNIFEBOT_ACTIVE"]):
            # draw white spot on the targeted player
            draw_spot(frame.line, read_game.screen_center_x + angle[0], read_game.screen_center_y + angle[1], BOT_FRAME_COLOR)

        if self.player_locked:
            if key_tubebot or key_knifebot:
                aim = self.player_locked.pos
                velocity = TUBE_VEL
                if key_knifebot:
                    velocity = KNIFE_VEL
                    aim.z += 40             # middle of body
                slope = self.find_slope(aim, read_game.my_pos, velocity)
                if not slope is None:
                    aim.z = read_game.my_pos.z + slope * (aim - read_game.my_pos).length()
                    spot_coord = read_game.world_to_screen(aim)
                    if spot_coord:
                        angle[0] = spot_coord.x - read_game.screen_center_x - 1      # -1 ?
                        angle[1] = spot_coord.y - read_game.screen_center_y
                        mouse_move(angle[0] / 3, angle[1] / 3, read_game.mouse_center_x, read_game.mouse_center_y)
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
                mouse_move(angle[0] / aim_speed, angle[1] / aim_speed, read_game.mouse_center_x, read_game.mouse_center_y)
            else:
                self.player_locked = None
        
        # debug mode calibration - aiming at (0,0,0) point
        if CALIBRATING:
            origin = VECTOR(0, 0, 0)
            spot_coord = read_game.world_to_screen(origin)
            if spot_coord:
                draw_spot(frame.line, spot_coord.x, spot_coord.y, 0x7FFFFFFF)
            if key_tubebot or key_knifebot:
                velocity = TUBE_VEL
                if key_knifebot:
                    velocity = KNIFE_VEL
                slope = self.find_slope(origin, read_game.my_pos, velocity)
                if not slope is None:
                    aim.z = read_game.my_pos.z + slope * (aim - read_game.my_pos).length()
                    spot_coord = read_game.world_to_screen(aim)
                    if spot_coord:
                        angle[0] = spot_coord.x - read_game.screen_center_x - 1      # -1 ?
                        angle[1] = spot_coord.y - read_game.screen_center_y
                        print "slope = %.3f, angle = %.3f, %.3f" % (slope, angle[0], angle[1])
                        mouse_move(angle[0] / 3, angle[1] / 3, read_game.mouse_center_x, read_game.mouse_center_y)
                

    @staticmethod
    def find_slope(target, player, vel):
        from math import sqrt
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

    @staticmethod
    def sq(x, y):
        return x*x + y*y
                        
