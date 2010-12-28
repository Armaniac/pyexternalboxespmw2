from Config import * #@UnusedWildImport
from ctypes import * #@UnusedWildImport
from structs import COD7_WeaponDesc, STR256, COD7_WeaponDesc_T
import re

WEAPON_PREFIX = "WEAPON_"
WEAPON_LIMIT = 1750         # size of array to be read
GRENADE_LAUNCHER_REGEXP = "(^gl_)|(^china_lake_)"
    
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
    
    def get_weapon_name(self, weaponnum):
        if self.weapon_names is None:
            return None
        else:
            return self.weapon_names[weaponnum]
    
    def get_weapon_model(self, weaponnum):
        if self.weapon_models is not None and weaponnum >= 0 and weaponnum < WEAPON_LIMIT:
            return self.weapon_models[weaponnum]
        return None
        
    def is_grenade_launcher(self, weaponnum):
        weapon_model = self.get_weapon_model(weaponnum)
        if weapon_model is not None:
            return self.gl_re.search(weapon_model)
        return False
    
    def is_sniper_rifle(self, weaponnum):
        return False
