from Config import * #@UnusedWildImport
from ctypes import * #@UnusedWildImport
from structs import COD7_WeaponDesc, STR256, COD7_WeaponDesc_T, AMMOMAX
import re
from directx.types import D3DRECT, D3DCLEAR
from utils import draw_string_center

WEAPON_PREFIX = "WEAPON_"
WEAPON_LIMIT = 1750         # size of array to be read
GRENADE_LAUNCHER_REGEXP = "(^gl_)|(^china_lake_)"

FRAG_GRENADES = ("frag_grenade_mp", "sticky_grenade_mp", "hatchet_mp")
TACT_GRENADES = ("willy_pete_mp", "concussion_grenade_mp", "flash_grenade_mp", "tabun_gas_mp", "nightingale_mp")
    
class WeaponNames(object):
    
    def __init__(self, env):
        self.env = env
        self.weapon_names = None
        self.weapon_models = None
        self.gl_re = re.compile(GRENADE_LAUNCHER_REGEXP)

    def render(self):
        offsets = self.env.offsets
        read_game = self.env.read_game
        if not read_game.is_in_game:
            self.weapon_names = None
            self.weapon_models = None
            return
        if self.weapon_models is not None:               # already populated
            frame = self.env.frame
            r = D3DRECT(read_game.resolution_x - 150, read_game.resolution_y - 160, read_game.resolution_x - 50, read_game.resolution_y - 140)
            #frame.device.Clear(1, byref(r), D3DCLEAR.TARGET, 0x7F000000, 1, 0)
            ammo_str = "%i" % self.get_ammo(self.get_current_weapon())
            draw_string_center(frame.rage_font, read_game.resolution_x - 200, read_game.resolution_y - 12, 0xE0000000, ammo_str)
            draw_string_center(frame.rage_font, read_game.resolution_x - 202, read_game.resolution_y - 14, 0xE0CFCF7F, ammo_str)
            return
        
        weapons = COD7_WeaponDesc()
        read_game._RPM(offsets.WEAPON_PTR, weapons)
        weapon = COD7_WeaponDesc_T()
        
        self.weapon_names = ["" for x in xrange(WEAPON_LIMIT)] #@UnusedVariable
        self.weapon_models = ["" for x in xrange(WEAPON_LIMIT)] #@UnusedVariable
        if DEBUG_PRINT_WEAPON_NAMES:
            dump = []
        
        try:
            str256 = STR256()
            for idx in range(WEAPON_LIMIT):
                addr = weapons.arr[idx]
                if addr != 0:
                    read_game._RPM(addr, weapon)
                    
                    read_game._RPM(weapon.model, str256)
                    model_name = string_at(addressof(str256))
                    self.weapon_models[idx] = model_name
                    
                    read_game._RPM(weapon.name_addr, str256)
                    weapon_name = string_at(addressof(str256))
                    if weapon_name.startswith(WEAPON_PREFIX):
                        weapon_name = weapon_name[len(WEAPON_PREFIX):]
                    self.weapon_names[idx] = weapon_name
                    
                    if DEBUG_PRINT_WEAPON_NAMES:
                        dump.append("%04i: %s" % (idx, model_name))
        finally:
            if DEBUG_PRINT_WEAPON_NAMES:
                for l in dump:
                    print l
                del dump
    def get_current_weapon(self):
        return self.env.read_game.my_player.weapon_num
    
    def get_weapon_name(self, weaponnum):
        if self.weapon_models is not None and weaponnum >= 0 and weaponnum < WEAPON_LIMIT:
            return self.weapon_names[weaponnum]
        return None
    
    def get_weapon_model(self, weaponnum):
        if self.weapon_models is not None and weaponnum >= 0 and weaponnum < WEAPON_LIMIT:
            return self.weapon_models[weaponnum]
        return None
        
    def is_grenade_launcher(self, weaponnum):
        return self.is_grenade_launcher_name(self.get_weapon_model(weaponnum))

    def is_grenade_launcher_name(self, weapon_model):
        if weapon_model is not None:
            return self.gl_re.search(weapon_model)
        return False
    
    def is_sniper_rifle(self, weaponnum):
        return False

    def get_ammo(self, weaponnum):      # get the ammo left for this weapon, None if weapon is not owned
        if weaponnum is None:
            return ""
        for i in range(AMMOMAX):
            ammo = self.env.read_game.cg.ammos[i]
            if weaponnum == ammo.weapon_id:
                return ammo.ammo
        return None
    
    def get_frag_grenade_model(self):
        for i in range(AMMOMAX):
            ammo_model = self.get_weapon_model(self.env.read_game.cg.ammos[i].weapon_id)
            if ammo_model in FRAG_GRENADES:
                return ammo_model;
        return None
        
    def get_tact_grenade_model(self):
        for i in range(AMMOMAX):
            ammo_model = self.get_weapon_model(self.env.read_game.cg.ammos[i].weapon_id)
            if ammo_model in TACT_GRENADES:
                return ammo_model;
        return None
        