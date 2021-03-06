from Config import * #@UnusedWildImport
from ctypes import * #@UnusedWildImport
from structs import MW2_WeaponDesc, STR256, MW2_WeaponDesc_T

    
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
        if self.weapon_names is not None:               # already populated
            # just check if RIOT_SHIELD has not moved since last time
            cur_riot_shield = self.get_riot_shield_num()
            str256 = STR256()
            weap_desc = MW2_WeaponDesc_T()
            read_game._RPM(WEAPON_DESC + cur_riot_shield * sizeof(MW2_WeaponDesc_T), weap_desc)
            str256 = STR256()
            addr = weap_desc.name_addr
            read_game._RPM(addr, str256)
            weapon_name = string_at(addressof(str256))
            model_name = string_at(addressof(str256) + len(weapon_name) + 1)
            if model_name.find("RIOTSHIELD") < 0:
                print "Reloading weapons"
            else:
                return

        
        weapons = MW2_WeaponDesc()
        read_game._RPM(WEAPON_DESC, weapons)
        
        self.weapon_names = ["" for x in xrange(1200)] #@UnusedVariable
        self.weapon_models = ["" for x in xrange(1200)] #@UnusedVariable
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
                    
                    self.weapon_names[idx] = weapon_name
                    self.weapon_models[idx] = model_name
                    
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
        
    def get_corrected_weapon_num(self, weapon_num):
        # considering riot is at #2
        return weapon_num - 2 + self.get_riot_shield_num()
    
    def get_riot_shield_num(self):
        for idx in range(10):
            if self.weapon_models[idx].find("RIOTSHIELD") >= 0:
                return idx
        return None