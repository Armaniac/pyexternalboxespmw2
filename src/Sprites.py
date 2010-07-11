from directx.d3d import IDirect3DTexture9
from directx.d3dx import d3dxdll
from ctypes import POINTER, byref
import os

SPRITES_FOLDER = "sprites\\"

SPRITES = { "WEAPON_CLAYMORE": "claymore.jpg",
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
            }

# 1176, 1175, 1174: AC-130 from big to small
# 1177 = predator
class Sprites(object):
    
    def __init__(self, env):
        self.env = env
        self.model_sprites = {}

    def init(self):
        frame = self.env.frame
        
        if os.path.isdir(SPRITES_FOLDER):
            for (model, file) in SPRITES.items():
                texture = POINTER(IDirect3DTexture9)()
                d3dxdll.D3DXCreateTextureFromFileA(frame.device,
                                                   SPRITES_FOLDER + file,
                                                   byref(texture))
                self.model_sprites[model] = texture
        else:
            raise Exception("'sprites' folder is not present!")
    
    def render(self):
        pass
    
    def get_sprite(self, model_name):
        return self.model_sprites.get(model_name)