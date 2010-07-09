from Config import *
from Keys import keys
from ctypes import *
from structs import MW2_WeaponDesc, STR256

    
class WeaponNames(object):
    
    def __init__(self, env):
        self.env = env
        self.weapon_names = None
        self.weapon_models = None

    def render(self):
        read_game = self.env.read_game
        if not read_game.is_in_game:
            self.weapon_names = None
            self.weapon_models = None
            return
        if self.weapon_names is not None: return            # already populated
        
        weapons = MW2_WeaponDesc()
        read_game._RPM(WEAPON_DESC, weapons)
        
        self.weapon_names = ["" for x in xrange(1200)]
        self.weapon_models = ["" for x in xrange(1200)]
        if DEBUG_PRINT_WEAPON_NAMES:
            dump = []
        
        try:
            str256 = STR256()
            for idx in range(1200):
                addr = weapons.arr[idx].name_addr
                if addr != 0:
                    read_game._RPM(addr, str256)
                    
                    weapon_name = string_at(addressof(str256))
                    model_name = string_at(addressof(str256) + len(weapon_name) + 1)
                    
                    self.weapon_names[idx+1] = weapon_name
                    self.weapon_models[idx+1] = model_name
                    
                    if DEBUG_PRINT_WEAPON_NAMES:
                        dump.append("%04i: %s / %s" % (idx, weapon_name, model_name))
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
        if self.weapon_names is None:
            return None
        else:
            return self.weapon_models[weaponnum]