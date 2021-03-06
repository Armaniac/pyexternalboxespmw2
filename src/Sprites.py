from ctypes import POINTER, byref, c_float
from Config import * #@UnusedWildImport
from directx.d3d import IDirect3DTexture9
from directx.d3dx import d3dxdll, D3DXVECTOR2, D3DMATRIX
import os
import math

SPRITES_FOLDER = "sprites\\"

SPRITES = { "WEAPON_CLAYMORE": "claymore.jpg",
            "WEAPON_CLAYMORE-friend": "claymore_friend.jpg",
            "WEAPON_C4": "c4.jpg",
            "WEAPON_FLASH_GRENADE": "flash.jpg",
            "WEAPON_M2FRAGGRENADE": "grenade.jpg",
            "WEAPON_SEMTEX": "semtex.jpg",
            "WEAPON_SMOKE_GRENADE": "smoke.jpg",
            "WEAPON_CONCUSSION_GRENADE": "stun.jpg",
            "WEAPON_THROWING_KNIFE": "knife.jpg",
            "WEAPON_M203": "nade.jpg",
            "WEAPON_M79": "nade.jpg",
            "WEAPON_AIRDROP_MARKER": "airdrop.jpg",
            "WEAPON_AIRDROP_SENTRY_MARKER": "sentry.jpg",
            "WEAPON_AIRDROP_MEGA_MARKER": "emergency.jpg",
            # Compass sprites for Radar
            "COMPASS_SENTRY_FRIEND": "sentry_friendly.png",
            "COMPASS_SENTRY_ENEMY": "sentry_enemy.png",
            "COMPASS_AC130_FRIEND": "ac130_green.png",
            "COMPASS_AC130_ENEMY": "ac130_red.png",
            "COMPASS_COBRA_FRIEND": "cobra_green.png",
            "COMPASS_COBRA_ENEMY": "cobra_red.png",
            "COMPASS_HARRIER_FRIEND": "harrier_green.png",
            "COMPASS_HARRIER_ENEMY": "harrier_red.png",
            "COMPASS_HELI_FRIEND": "heli_green.png",
            "COMPASS_HELI_ENEMY": "heli_red.png",
            "COMPASS_LITTLEBIRD_FRIEND": "littlebird_green.png",
            "COMPASS_LITTLEBIRD_ENEMY": "littlebird_red.png",
            "COMPASS_PAVELOW_FRIEND": "pavelow_green.png",
            "COMPASS_PAVELOW_ENEMY": "pavelow_red.png",
            #
            "COMPASS_FLARE": "flare.png",
            }

HELIS = { 1181: "COMPASS_HARRIER",
          1183: "COMPASS_LITTLEBIRD",
          1184: "COMPASS_HELI",
          1185: "COMPASS_PAVELOW",
          1186: "COMPASS_HELI",     # apache
         }
# if riot == 2
# 1176, 1175, 1174: AC-130 from big to small
# 1177 = predator

# 766 WEAPON_JAVELIN
# 763 WEAPON_RPG
# WEAPON_AT4_LOCKAIR
# WEAPON_STINGER

D3DXSPRITE_ALPHABLEND = (1 << 4)
SPRITE_SIZE = 32

class Sprites(object):
    
    def __init__(self, env):
        self.env = env
        self.model_sprites = {}

    def init(self):
        frame = self.env.frame
        
        if os.path.isdir(SPRITES_FOLDER):
            for (model, file) in SPRITES.items():
                texture = POINTER(IDirect3DTexture9)()
                d3dxdll.D3DXCreateTextureFromFileA(frame.device, #@UndefinedVariable
                                                   SPRITES_FOLDER + file,
                                                   byref(texture))
                self.model_sprites[model] = texture
        else:
            raise Exception("'sprites' folder is not present!")
    
    def render(self):
        pass
    
    def get_sprite(self, model_name):
        return self.model_sprites.get(model_name)

    def draw_sprite(self, model_name, x, y, angle, color, scaling):
        frame = self.env.frame
        sprite = self.get_sprite(model_name)
        if sprite:
            frame.sprite.Begin(D3DXSPRITE_ALPHABLEND)
            sprite_center = D3DXVECTOR2(16, 16)
            trans = D3DXVECTOR2(x- SPRITE_SIZE*scaling/2, y- SPRITE_SIZE*scaling/2)
            matrix = D3DMATRIX()
            d3dxdll.D3DXMatrixAffineTransformation2D(byref(matrix), #@UndefinedVariable
                                                     c_float(scaling),          # scaling
                                                     byref(sprite_center),      # rotation center
                                                     c_float(math.radians(angle)),                # angle
                                                     byref(trans)               # translation
                                                     )
            frame.sprite.SetTransform(matrix)
            frame.sprite.Draw(sprite, None, None, None, color)
            frame.sprite.End()

    def draw_sentry(self, x, y, enemy):
        if enemy is None:
            pass
        elif enemy:
            self.draw_sprite("COMPASS_SENTRY_ENEMY", x, y, 0, COLOR_MAP_BLENDER_ENEMY, 0.5)
        else:
            self.draw_sprite("COMPASS_SENTRY_FRIEND", x, y, 0, COLOR_MAP_BLENDER_FRIEND, 0.5)
            
    def draw_heli(self, x, y, yaw, enemy, weapon_num):
        if enemy is None:
            return
        weapon_names = self.env.weapon_names
        weapon_num_corrected = weapon_names.get_corrected_weapon_num(weapon_num)
        model_name = HELIS.get(weapon_num_corrected)
        if not model_name:
            model_name = "COMPASS_HELI"
        if enemy:
            self.draw_sprite(model_name + "_ENEMY", x, y, yaw, COLOR_MAP_BLENDER_ENEMY, 1.0)
        else:
            self.draw_sprite(model_name + "_FRIEND", x, y, yaw, COLOR_MAP_BLENDER_FRIEND, 1.0)
            
    def draw_plane(self, x, y, yaw, enemy):
        # don't know how to determine enemy...
        self.draw_sprite("COMPASS_HARRIER_ENEMY", x, y, yaw, COLOR_MAP_BLENDER_ENEMY, 1.0)
    
    def draw_flare(self, x, y):
        self.draw_sprite("COMPASS_FLARE", x, y, 0, COLOR_MAP_BLENDER_NEUTRAL, 0.5)