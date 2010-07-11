from ctypes import byref, cast, POINTER, c_int, pointer
from Config import *
from utils import draw_box, draw_line_abs, draw_string_center, draw_spot
from structs import VECTOR, FLAGS_CROUCHED, FLAGS_PRONE, ET_PLAYER, ET_TURRET, ET_EXPLOSIVE, ET_HELICOPTER, ET_PLANE, PLAYERMAX
from directx.d3dx import D3DRECT, D3DCLEAR, D3DXVECTOR2, D3DXVECTOR3
from Keys import keys
from ctypes import windll

KEYEVENTF_KEYUP = 0x0002

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
                        distance = (p.pos - read_game.my_player.pos).length()
                        if FADE_ENABLED:
                            # now adapt alpha level to distance
                            if distance > FADE_MAX_DIST:
                                alpha = FADE_MAX_ALPHA
                            elif distance < FADE_MIN_DIST:
                                alpha = FADE_MIN_ALPHA
                            else:
                                alpha = ((distance-FADE_MIN_DIST)*FADE_MAX_ALPHA + (FADE_MAX_DIST-distance)*FADE_MIN_ALPHA) / (FADE_MAX_DIST-FADE_MIN_DIST)
                            p.color_esp = (p.color_esp & 0x00FFFFFF) | (int(alpha) << 24)
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
                            draw_string_center(frame.font, feet.x, feet.y - size_y, COLOR_PLAYER_NAME, p.name)
                        if keys["KEY_BOX_SNAPLINE"] and p.enemy and p.alive & 0x0001:
                            draw_line_abs(frame.line, read_game.screen_center_x, read_game.resolution_y,
                                  feet.x, feet.y, COLOR_BOX_LINE_WIDTH, p.color_esp)      # w/h ratio
                        if keys["KEY_BOXESP"]:
                            converted_distance = distance * DISTANCE_ESP_UNIT
                            distance_str = "%i %s" % (converted_distance, DISTANCE_ESP_UNIT_NAME)
                            draw_string_center(frame.font, feet.x, feet.y + 12, COLOR_PLAYER_NAME, distance_str)
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
        for e in read_game.mw2_entity.arr:
            #e = read_game.mw2_entity.arr[i]
            if e.type == ET_TURRET and e.alive & 0x0001 and keys["KEY_BOXESP"]:
                head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 20)       # eyepos of standing player
                feet = read_game.world_to_screen(e.pos)
                head = read_game.world_to_screen(head_pos)
                if feet and head:
                    size_y = feet.y - head.y
                    if size_y < 5:  size_y = 5
                    size_x = size_y / 2.75
                    draw_box(frame.line, feet.x - size_x/2, feet.y, size_x, -size_y, COLOR_BOX_OUTER_WIDTH, COLOR_SENTRY)
                    
            elif keys["KEY_EXPLOSIVES"] and e.type == ET_EXPLOSIVE and e.alive & 0x0001:
                head_pos = VECTOR(e.pos.x, e.pos.y, e.pos.z + 10)       # eyepos of standing player
                feet = read_game.world_to_screen(e.pos)
                head = read_game.world_to_screen(head_pos)
                if feet and head:
                    size_y = feet.y - head.y
                    if size_y < 8:  size_y = 8
                    model_name = weapon_names.get_weapon_model(e.WeaponNum)
                    sprite = self.env.sprites.get_sprite(model_name)
                    if sprite:
                        frame.sprite.Begin(0)
                        #frame.sprite.SetTransform(matrix)
                        sprite_center = D3DXVECTOR3(8, 8, 0)
                        where = D3DXVECTOR3(feet.x-8, feet.y-8, 0)
                        frame.sprite.Draw(sprite, None, byref(sprite_center), byref(where), 0xAF7F7F7F)
                        frame.sprite.End()
                        distance = (e.pos - read_game.my_player.pos).length()
                        converted_distance = distance * DISTANCE_ESP_UNIT
                        distance_str = "%i %s" % (converted_distance, DISTANCE_ESP_UNIT_NAME)
                        draw_string_center(frame.font, feet.x, feet.y + 20, COLOR_CLAYMORE, distance_str)
                    else:
                        r = D3DRECT(int(feet.x-8), int(feet.y-16), int(feet.x+8), int(feet.y))
                        frame.device.Clear(1, byref(r), D3DCLEAR.TARGET, COLOR_CLAYMORE, 1, 0)
                    
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