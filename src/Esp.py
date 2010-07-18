from ctypes import byref, cast, POINTER, c_int, pointer, c_float
from Config import *
from utils import draw_box, draw_line_abs, draw_string_center, draw_spot
from structs import VECTOR, FLAGS_CROUCHED, FLAGS_PRONE, ET_PLAYER, ET_TURRET, ET_EXPLOSIVE, ET_HELICOPTER, ET_PLANE, PLAYERMAX, ENTITIESMAX, EntityTracker
from directx.d3d import D3DMATRIX
from directx.d3dx import D3DRECT, D3DCLEAR, D3DXVECTOR3, d3dxdll, D3DXVECTOR2
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
        
        if keys["KEY_BOXESP"]:
            for idx in range(PLAYERMAX):
                p = read_game.player[idx]
                if (p.type == ET_PLAYER) and p.valid and p.alive and p != read_game.my_player:
                    # colors already calculated
                    head_pos = VECTOR(p.pos.x, p.pos.y, p.pos.z + 60)       # eyepos of standing player
                    feet = read_game.world_to_screen(p.pos)
                    head = read_game.world_to_screen(head_pos)
                    if feet and head:
                        p.color_esp = self.get_faded_color(p.pos, p.color_esp)
                        size_y = feet.y - head.y
                        size_x = size_y / 2.75          # standing up
                        if size_y < 10:     size_y = 10
                        if p.pose & FLAGS_CROUCHED:
                            size_y /= 1.5
                            size_x = size_y / 1.5       # w/h ratio
                        elif p.pose & FLAGS_PRONE:
                            size_y /= 3
                            size_x = size_y * 2         # w/h ratio
                        if keys["KEY_BOXESP"]:
                            if keys["KEY_SPOT23_ESP"]:
                                p3 = read_game.mw2_entity.arr[idx].pos3
                                pos3 = VECTOR(p3.x, p3.y, p3.z + 55)
                                head3 = read_game.world_to_screen(pos3)
                                if head3:
                                    draw_spot(frame.line, head3.x, head3.y, 0x7FC00000)
                                p2 = read_game.mw2_entity.arr[idx].pos2
                                pos2 = VECTOR(p2.x, p2.y, p2.z + 55)
                                head2 = read_game.world_to_screen(pos2)
                                if head2:
                                    draw_spot(frame.line, head2.x, head2.y, 0x80FFBF00)
                            draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, p.color_esp)
                            if keys["KEY_WEAPON_ESP"]:
                                name_esp_str = "%s [%s]" % (p.name, weapon_names.get_weapon_name(p.weapon_num))
                            else:
                                name_esp_str = p.name
                            draw_string_center(frame.font, feet.x, feet.y - size_y, COLOR_PLAYER_NAME, name_esp_str)
                        if keys["KEY_BOX_SNAPLINE"] and p.enemy and p.alive & 0x0001:
                            draw_line_abs(frame.line, read_game.screen_center_x, read_game.resolution_y,
                                  feet.x, feet.y, COLOR_BOX_LINE_WIDTH, p.color_esp)      # w/h ratio
                        if keys["KEY_BOXESP"]:
                            self.draw_distance_ESP(p.pos, feet.x, feet.y, COLOR_PLAYER_NAME)
                        if keys["KEY_TRIGGERBOT"] and keys["KEY_TRIGGER_BOT_KEY"]:
                            if p.alive & 0x0001 and p.enemy and p.pose != 0:
                                if (read_game.screen_center_x > feet.x - size_x/2) and (read_game.screen_center_x < feet.x + size_x/2):
                                    if (read_game.screen_center_y > feet.y - size_y) and (read_game.screen_center_y < feet.y ):
                                        #print "try trigger bot"
                                        if self.env.ticks - self.last_trigger_tick > 5:
                                            #print "triggerbot fire"
                                            self.last_trigger_tick = self.env.ticks
                                            windll.User32.keybd_event(TRIGGER_BOT_FIRE_KEY, 0x12, 0, 0)
                                            windll.User32.keybd_event(TRIGGER_BOT_FIRE_KEY, 0x12, KEYEVENTF_KEYUP, 0)
                            
                            
        
        #=======================================================================
        # pp = cast(pointer(read_game.mw2_entity), POINTER(c_int))
        # for i in range(ENTITIESMAX):
        #    #type = pp[0xE0/4 + 0x204/4*i]
        #    type = pp[0x38 + 0x81*i]
        #    if type == ET_TURRET or type == ET_EXPLOSIVE or type==ET_HELICOPTER or type==ET_PLANE:
        #=======================================================================
        for idx in range(ENTITIESMAX):
            e = read_game.mw2_entity.arr[idx]
            if e.type == ET_TURRET and e.alive & 0x0001 and keys["KEY_BOXESP"]:
                head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 20)       # eyepos of standing player
                feet = read_game.world_to_screen(e.pos)
                head = read_game.world_to_screen(head_pos)
                if feet and head:
                    size_y = feet.y - head.y
                    if size_y < 5:  size_y = 5
                    size_x = size_y / 2.75
                    draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, COLOR_SENTRY)
                    
            elif e.type == ET_EXPLOSIVE and e.alive & 0x0001:
                #self.draw_explosive(e)
                self.track_explosive(idx)
                    
            elif (e.type == ET_HELICOPTER or e.type == ET_PLANE) and e.alive & 0x0001 and keys["KEY_BOXESP"]:
                head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 100)       # eyepos of standing player
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
                        
        self.loop_tracked_explo()
    
    def track_explosive(self, idx):
        te = self.env.tracker.track_entity(idx)
        if te and te.model_name.find("_AIRDROP_") > 0:
            te.endoflife = self.env.read_game.game_time + int(AIRDROP_PERSISTENCE*1000)

    def loop_tracked_explo(self):
        for te in self.env.tracker.get_tracked_entity_list():
            if te.type == ET_EXPLOSIVE:
                self.draw_tracked_explo(te)

    def draw_tracked_explo(self, te):
        read_game = self.env.read_game
        frame = self.env.frame

        head_pos = VECTOR(te.pos.x, te.pos.y, te.pos.z + 10)
        feet = read_game.world_to_screen(te.pos)
        head = read_game.world_to_screen(head_pos)
        if feet and head:
            # claymore friend tracking
            if te.model_name == "WEAPON_CLAYMORE":
                if not te.planter.enemy:
                    te.model_name = "WEAPON_CLAYMORE-friend"
            size_y = feet.y - head.y
            if size_y < 12:  size_y = 12.0
            sprite = self.env.sprites.get_sprite(te.model_name)
            if sprite:
                frame.sprite.Begin(0)
                scaling = size_y / float(_EXPLO_SPRITE_SIZE)
                sprite_center = D3DXVECTOR2(0, 0)
                trans = D3DXVECTOR2(feet.x - _EXPLO_SPRITE_SIZE*scaling/2, feet.y - _EXPLO_SPRITE_SIZE*scaling)
                matrix = D3DMATRIX()
                d3dxdll.D3DXMatrixAffineTransformation2D(byref(matrix),
                                                         c_float(scaling),          # scaling
                                                         byref(sprite_center),      # rotation center
                                                         c_float(0),                # angle
                                                         byref(trans)               # translation
                                                         )
                frame.sprite.SetTransform(matrix)
                frame.sprite.Draw(sprite, None, None, None, COLOR_CLAYMORE_SPRITE)
                frame.sprite.End()
                self.draw_distance_ESP(te.pos, feet.x, feet.y, COLOR_CLAYMORE_DISTANCE)
            else:
                pass
                #print "unknown explosive model:%s (%i)" % (model_name, e.WeaponNum)
                #r = D3DRECT(int(feet.x-8), int(feet.y-16), int(feet.x+8), int(feet.y))
                #frame.device.Clear(1, byref(r), D3DCLEAR.TARGET, COLOR_CLAYMORE, 1, 0)
                
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
        converted_distance = distance * DISTANCE_ESP_UNIT
        distance_str = "%i %s" % (converted_distance, DISTANCE_ESP_UNIT_NAME)
        draw_string_center(self.env.frame.font, x, y + 12, color, distance_str)