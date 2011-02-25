from Config import * #@UnusedWildImport
from utils import draw_box, draw_line_abs, draw_string_center
from structs import VECTOR, FLAGS_CROUCHED, FLAGS_PRONE, ET_PLAYER, ET_TURRET, ET_EXPLOSIVE, ET_HELICOPTER, ET_PLANE, PLAYERMAX, ENTITIESMAX, ALIVE_FLAG, ET_VEHICLE
from structs import RECT, DOGSMAX
from Keys import keys
from ctypes import windll

KEYEVENTF_KEYUP = 0x0002
_EXPLO_SPRITE_SIZE = 32

class Esp(object):
    
    def __init__(self, env):
        self.env = env
        self.last_trigger_tick = 0
    
    def render(self):
        read_game = self.env.read_game
        frame = self.env.frame
        weapon_names = self.env.weapon_names
        if not read_game.is_in_game: return
        
        # enemy behind indicators
        enemy_behind = enemy_left = enemy_right = False

        if keys["KEY_BOXESP"]:
            for idx in range(PLAYERMAX):
                p = read_game.player[idx]
                if (p.type == ET_PLAYER) and p.valid and p.alive and p != read_game.my_player:
                    # colors already calculated
                    feet, head, size_x, size_y = self.calc_size_xy(p)
                    if feet and head:
                        p.color_esp = self.get_faded_color(p.pos, p.color_esp)

                        if keys["KEY_BOXESP"]:
                            draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, p.color_esp)
                            if keys["KEY_WEAPON_ESP"]:
                                name_esp_str = "%s [%s]" % (p.name, weapon_names.get_weapon_model(p.weapon_num))
                            else:
                                name_esp_str = p.name
                            draw_string_center(frame.font, feet.x, feet.y - size_y, COLOR_PLAYER_NAME, name_esp_str)
                        if keys["KEY_BOX_SNAPLINE"] and p.enemy and p.alive & ALIVE_FLAG:
                            draw_line_abs(frame.line, read_game.screen_center_x, read_game.resolution_y,
                                  feet.x, feet.y, COLOR_BOX_LINE_WIDTH, p.color_esp)      # w/h ratio
                        if keys["KEY_BOXESP"]:
                            self.draw_distance_ESP(p.pos, feet.x, feet.y, COLOR_PLAYER_NAME)
                        if keys["KEY_TRIGGERBOT"] and keys["KEY_TRIGGER_BOT_KEY"]:
                            if p.alive & ALIVE_FLAG and p.enemy and p.pose != 0:
                                if (read_game.screen_center_x > feet.x - size_x/4) and (read_game.screen_center_x < feet.x + size_x/4):
                                    if (read_game.screen_center_y > feet.y - size_y) and (read_game.screen_center_y < feet.y ):
                                        if self.env.ticks - self.last_trigger_tick > 5:
                                            self.last_trigger_tick = self.env.ticks
                                            windll.User32.keybd_event(ord(TRIGGER_BOT_FIRE_KEY), 0x12, 0, 0)
                                            windll.User32.keybd_event(ord(TRIGGER_BOT_FIRE_KEY), 0x12, KEYEVENTF_KEYUP, 0)
                    else:
                        # check if we need to show enemy behind indicator
                        transform = read_game.world_to_screen_transform(p.pos)
                        if transform.z < 10 and p.enemy:
                            if abs(transform.x / transform.z) < 1:
                                enemy_behind = True
                            elif transform.x > 0:
                                enemy_left = True
                            else:
                                enemy_right = True


                            
        if keys["KEY_ENEMY_BEHIND"] and (enemy_behind or enemy_left or enemy_right):
            sprites = self.env.sprites
            if enemy_behind:
                sprites.draw_sprite("down", read_game.screen_center_x, read_game.screen_center_y + ENEMY_BEHIND_Y,
                                    0, ENEMY_BEHIND_COLOR_BLEND, ENEMY_BEHIND_SCALING)
            if enemy_left:
                sprites.draw_sprite("left-down", read_game.screen_center_x - ENEMY_BEHIND_X, read_game.screen_center_y + ENEMY_BEHIND_Y,
                                    0, ENEMY_BEHIND_COLOR_BLEND, ENEMY_BEHIND_SCALING)
            if enemy_right:
                sprites.draw_sprite("right-down", read_game.screen_center_x + ENEMY_BEHIND_X, read_game.screen_center_y + ENEMY_BEHIND_Y,
                                    0, ENEMY_BEHIND_COLOR_BLEND, ENEMY_BEHIND_SCALING)
                    

        for idx in range(ENTITIESMAX):
            e = read_game.cod7_entity.arr[idx]
            
            if e.type == ET_TURRET and e.alive & ALIVE_FLAG and keys["KEY_BOXESP"]:
                self.env.tracker.track_entity(idx)
                head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 20)       # eyepos of standing player
                feet = read_game.world_to_screen(e.pos)
                head = read_game.world_to_screen(head_pos)
                if feet and head:
                    size_y = feet.y - head.y
                    if size_y < 5:  size_y = 5
                    size_x = size_y / 2.75
                    draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, COLOR_SENTRY)
#                if e.owner_turret >= 0 and e.owner_turret < PLAYERMAX:
#                    self.env.tracker.track_entity(idx, e.owner_turret)
#                    if read_game.player[e.owner_turret].enemy:
#                        head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 20)       # eyepos of standing player
#                        feet = read_game.world_to_screen(e.pos)
#                        head = read_game.world_to_screen(head_pos)
#                        if feet and head:
#                            size_y = feet.y - head.y
#                            if size_y < 5:  size_y = 5
#                            size_x = size_y / 2.75
#                            draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, COLOR_SENTRY)

            if e.type == ET_EXPLOSIVE and e.alive & ALIVE_FLAG:
                self.track_explosive(idx)
            
            elif e.type == ET_VEHICLE and e.alive & ALIVE_FLAG:
                if weapon_names.get_weapon_model(e.weapon) == "rc_car_weapon_mp":      # RC-XD
                    self.env.tracker.track_rcxd(idx)

            elif (e.type == ET_HELICOPTER or e.type == ET_PLANE) and e.alive & ALIVE_FLAG and keys["KEY_BOXESP"]:
                # all planes are shown because we don't know if they are enemies                
                self.env.tracker.track_entity(idx)
                head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 100)
                feet = read_game.world_to_screen(e.pos)
                head = read_game.world_to_screen(head_pos)
                if feet and head:
                    size_y = feet.y - head.y
                    if size_y < 10:  size_y = 10
                    size_x = size_y
                    draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, COLOR_PLANE)
                    if keys["KEY_BOX_SNAPLINE"]:
                        draw_line_abs(frame.line, read_game.screen_center_x, read_game.resolution_y,
                              feet.x, feet.y, COLOR_BOX_LINE_WIDTH, COLOR_PLANE)
                        
#            elif (e.type == ET_HELICOPTER or e.type == ET_PLANE) and e.alive & ALIVE_FLAG and keys["KEY_BOXESP"]:
#                if e.owner_air >= 0 and e.owner_air < PLAYERMAX:
#                    self.env.tracker.track_entity(idx, e.owner_air)
#                    if e.type == ET_PLANE or read_game.player[e.owner_air].enemy:
#                        # all planes are shown because we don't know if they are enemies
#                        head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 100)       # eyepos of standing player
#                        feet = read_game.world_to_screen(e.pos)
#                        head = read_game.world_to_screen(head_pos)
#                        if feet and head:
#                            size_y = feet.y - head.y
#                            if size_y < 10:  size_y = 10
#                            size_x = size_y
#                            draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, COLOR_PLANE)
#                            if keys["KEY_BOX_SNAPLINE"]:
#                                draw_line_abs(frame.line, read_game.screen_center_x, read_game.resolution_y,
#                                      feet.x, feet.y, COLOR_BOX_LINE_WIDTH, COLOR_PLANE)
#
        if keys["KEY_DOGS_ESP"]:
            for idx in range(DOGSMAX):
                dog = read_game.cod7_dog.arr[idx]
                client_num = dog.client_num             # the entity number holding the dog
                if client_num > 0 and client_num < ENTITIESMAX:     # let's look the real entity
                    e = read_game.cod7_entity.arr[client_num]
                    if e.alive & ALIVE_FLAG:
                        if DEBUG:
                            print "Found living dog idx=%i, clientnum=%i, owner=%i, team=%i"
                            self.env.inspector.dump_entity(client_num)
                        self.env.tracker.track_dog(client_num)
                                    
        self.loop_tracked_explo()
    
    def calc_size_xy(self, p, height = 60):                     # eyepos of standing player
        head_pos = VECTOR(p.pos.x, p.pos.y, p.pos.z + height)
        feet = self.env.read_game.world_to_screen(p.pos)
        head = self.env.read_game.world_to_screen(head_pos)
        size_x = 0
        size_y = 0
        if feet and head:
            size_y = feet.y - head.y
            size_x = size_y / 2.75          # standing up
            if size_y < 10:     size_y = 10
            if p.pose & FLAGS_CROUCHED:
                size_y /= 1.5
                size_x = size_y / 1.5       # w/h ratio
            elif p.pose & FLAGS_PRONE:
                size_y /= 3
                size_x = size_y * 2         # w/h ratio
        return (feet, head, size_x, size_y)

    def calc_player_rect(self, p):
        feet, head, size_x, size_y = self.calc_size_xy(p)
        if feet and head:
            return RECT(int(feet.x - size_x/2), int(feet.y - size_y), int(feet.x + size_x/2), int(feet.y))
        return None
    
    def calc_tracked_rect(self, te, height = 20):
        head_pos = VECTOR(te.pos.x, te.pos.y, te.pos.z + height)
        feet = self.env.read_game.world_to_screen(te.pos)
        head = self.env.read_game.world_to_screen(head_pos)
        size_x = 0
        size_y = 0
        if feet and head:
            size_y = feet.y - head.y
            if size_y < 10:     size_y = 10
            size_x = size_y                 # let's do it square
            return RECT(int(feet.x - size_x/2), int(feet.y - size_y), int(feet.x + size_x/2), int(feet.y))
    
    def track_explosive(self, idx):
        te = self.env.tracker.track_entity(idx)
        if te is not None and not self.env.sprites.get_sprite(te.model_name):
            if DEBUG:   print "Tracking explosive idx=%i, weapon=%i, name=%s" % (idx, te.weapon_num, te.model_name)

    def loop_tracked_explo(self):
        for te in self.env.tracker.get_tracked_entity_list():
            if te.type == ET_EXPLOSIVE or te.type == ET_VEHICLE:
                self.draw_tracked_explo(te)

    def draw_tracked_explo(self, te):
        read_game = self.env.read_game

        head_pos = VECTOR(te.pos.x, te.pos.y, te.pos.z + 10)
        feet = read_game.world_to_screen(te.pos)
        head = read_game.world_to_screen(head_pos)
        if feet and head:
            if te.model_name == "rc_car_weapon_mp" and te.enemy:
                te.model_name = "rc_car_weapon_mp-enemy"
            if te.model_name == "claymore_mp" and te.enemy:
                te.model_name = "claymore_mp-enemy"
            size_y = feet.y - head.y
            if size_y < 12:  size_y = 12.0
            
            if self.env.sprites.draw_sprite(te.model_name, feet.x, feet.y, 0.0, COLOR_CLAYMORE_SPRITE, size_y / float(_EXPLO_SPRITE_SIZE)):
                self.draw_distance_ESP(te.pos, feet.x, feet.y, COLOR_CLAYMORE_DISTANCE)
                
    def get_faded_color(self, pos, color):
        if FADE_ENABLED:
            distance = (pos - self.env.read_game.my_player.pos).length()
            # now adapt alpha level to distance
            if distance > FADE_MAX_DIST:
                alpha = FADE_MAX_ALPHA
            elif distance < FADE_MIN_DIST:
                alpha = FADE_MIN_ALPHA
            else:
                alpha = ((distance-FADE_MIN_DIST)*FADE_MAX_ALPHA + (FADE_MAX_DIST-distance)*FADE_MIN_ALPHA) / (FADE_MAX_DIST-FADE_MIN_DIST)
            return (color & 0x00FFFFFF) | (int(alpha) << 24)
        else:
            return color
        
    
    def draw_distance_ESP(self, pos, x, y, color):
        distance = (pos - self.env.read_game.my_player.pos).length()
        converted_distance = int(distance * DISTANCE_ESP_UNIT)
        distance_str = "%i %s" % (converted_distance, DISTANCE_ESP_UNIT_NAME)
        draw_string_center(self.env.frame.font, x, y + 12, color, distance_str)
