from binascii import unhexlify, hexlify
import re
from Config import * #@UnusedWildImport
from ctypes import create_string_buffer, windll, byref, sizeof, addressof, c_int
from utils import ExitingException
from struct import unpack

PATTERN_START_ADDR = 0x00401000
PATTERN_LEN = 0x00700000
PATTERN_MATCH = unhexlify('FF')


#Entities 2AC840DC
#from D2F970
#
#CG_T 2AB98100
#from D2C790
#
#CG_ST 2AC09700
#from D2C760

# for Sensitivity finder
# "sensitivity" string: => A1951B, string is at +1   0xA1951C

FIND_PATTERNS = { 
#                  'CG_ClientFrame':             ("83ec3453555657e800000000",
#                                                 "FFFFFFFFFFFFFFFF00000000"),
#                  'getWeaponinfo':              ("8b4424048b0c85000000008b4108c3",
#                                                 "FFFFFFFFFFFFFF00000000FFFFFFFF"),
                  'sensitivity_str':             ("0073656E736974697669747900",
                                                  "FFFFFFFFFFFFFFFFFFFFFFFFFF"),
                  'sensitivity_dvar':            ("6800000000E800000000D9050000000083C41868000000006A0183EC0CD95C2408A300000000",
                                                  "FFFFFFFFFFFF00000000FFFF00000000FFFFFFFF00000000FFFFFFFFFFFFFFFFFFFF00000000"),
                  'weapons':                     ("8B5424048B0D0000000033C08D6424003B1485000000007407403BC176F233C0C3",
                                                  "FFFFFFFFFFFF00000000FFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFFFFFF"),
                  'cg_t':                        ("8B4424088B0D0000000089818C150700C3",
                                                  "FFFFFFFFFFFF00000000FFFFFFFFFFFFFF"),
                  'cgs_t':                       ("8B4424088B0D0000000083EC24568BB481",
                                                  "FFFFFFFFFFFF00000000FFFFFFFFFFFFFF"),
                }

class PatternFinder(object):
    
    def __init__(self, env):
        self.env = env
        self.addr = {}

    def _find_pattern(self, buf, data, mask):
        # first compile the regex correponding to the mask
        pattern_escape = ''
        for i in range(len(data)):
            if mask[i] == PATTERN_MATCH:
                pattern_escape += re.escape(data[i])      # match the exact byte
            else:
                pattern_escape += '.'                       # match any byte
        res = list(re.finditer(pattern_escape, buf, re.DOTALL))    # DOTALL so '.' matches newlines
        return [ f.start() for f in res ]
        
    def find_patterns(self, process_handle):
        buf = create_string_buffer(PATTERN_LEN)
        self._RPM(process_handle, PATTERN_START_ADDR, buf)
        raw = buf.raw
        
        for name,l in FIND_PATTERNS.items():
            (data, mask) = l
            res = self._find_pattern(raw, unhexlify(data), unhexlify(mask))
            if len(res) == 0:
                print "%s not found" % (name,)
            elif len(res) > 1:
                print "%s duplicate finds: %s" % (name, " ".join([ "%x" % x for x in res]))
            else:
                addr = PATTERN_START_ADDR + res[0]
                self.addr[name] = addr
                print "%s found: 0x%x" % (name, addr)
        
        print "----------------------------------------"
        
        print "Finding Sensitivity location, string is at location 0x%x" % self.addr['sensitivity_str']
        sensitivity_dvar_pattern = FIND_PATTERNS['sensitivity_dvar'][0]
        sensitivity_dvar_mask = FIND_PATTERNS['sensitivity_dvar'][1]
        sensitivity_ptr = hexlify(c_int(self.addr['sensitivity_str'] + 1))     # skipping leading 00
        sensitivity_dvar_pattern = sensitivity_dvar_pattern[:2] + sensitivity_ptr + sensitivity_dvar_pattern[10:]
        res = self._find_pattern(raw, unhexlify(sensitivity_dvar_pattern), unhexlify(sensitivity_dvar_mask))
        if len(res) == 1:
            sensitivity_dvar_code = PATTERN_START_ADDR + res[0]
            print "Sensitivity DVAR code found 0x%x" % sensitivity_dvar_code
            sensitivity_dvar_ptr = self._get_int_in_raw(raw, sensitivity_dvar_code + 34)
            print "Sensitivity DVAR found 0x%x, should be 0x%x" % (sensitivity_dvar_ptr, SENSITIVITY_DVAR)
        
        weapons_ptr = self._get_int_in_raw(raw, self.addr["weapons"] + 19)
        print "Found Weapons 0x%x, should be 0x%x" % (weapons_ptr, WEAPON_PTR)
        
        cg_t_ptr = self._get_int_in_raw(raw, self.addr["cg_t"] + 6)
        cg_t = self._RPM_int(process_handle, cg_t_ptr)
        print "Found CG_T ptr 0x%x and 0x%x, should be 0x%x" % (cg_t_ptr, cg_t, CG_T)
        
        cgs_t_ptr = self._get_int_in_raw(raw, self.addr["cgs_t"] + 6)
        cgs_t = self._RPM_int(process_handle, cgs_t_ptr)
        print "Found CGS_T ptr 0x%x and 0x%x, should be 0x%x" % (cgs_t_ptr, cgs_t, CGS_T)
        
        return
        addr = self.addr["cvar"]
        self.cvar_phys_drawDebugInfo = self._get_int_in_raw(raw, addr + 1)
        self.ptr_access_phys_drawDebugInfo = addr + 5
        self.ptr_jmpto_phys_drawDebugInfo = addr + 20
        
        self.GetTagInfoForClientNum = self.addr["GetTagInfoForClientNum"]
        self.GetTagForClientNumInfo = self.addr["GetTagForClientNumInfo"]
        
        self.CG_Trace = self.addr["CG_Trace"]
        self.cg_time = self._get_int_in_raw(raw, self.addr["cg_time"] + 12) 
        self.ps_clientNum = self._get_int_in_raw(raw, self.addr["ps_clientNum"] + 1)
        self.refdef = self._get_int_in_raw(raw, self.addr["refdef"] + 14)
        self.dvars = self._get_int_in_raw(raw, self.addr["dvars"] + 8)
        self.num_dvars = self._get_int_in_raw(raw, self.addr["dvars"] + 31)
        self.centity_t_size = self._get_int_in_raw(raw, self.addr["cg_entities"] + 10)
        self.cg_entities = self._get_int_in_raw(raw, self.addr["cg_entities"] + 20)
        
        print "cvar_phys_drawDebugInfo=%x" % self.cvar_phys_drawDebugInfo
        print "ptr_access_phys_drawDebugInfo=%x" % self.ptr_access_phys_drawDebugInfo
        print "ptr_jmpto_phys_drawDebugInfo=%x" % self.ptr_jmpto_phys_drawDebugInfo
        print "GetTagInfoForClientNum=%x" % self.GetTagInfoForClientNum
        print "GetTagForClientNumInfo=%x" % self.GetTagForClientNumInfo
        print "CG_Trace=%x" % self.CG_Trace
        print "cg_time=%x" % self.cg_time
        print "ps_clientNum=%x" % self.ps_clientNum
        print "refdef=%x" % self.refdef
        print "dvars=%x" % self.dvars
        print "num_dvars=%x" % self.num_dvars
        print "centity_t_size=%x" % self.centity_t_size
        print "cg_entities=%x" % self.cg_entities
        
    def _RPM(self, process_handle, address, buffer):
        if not windll.kernel32.ReadProcessMemory(process_handle, address, byref(buffer), sizeof(buffer), None): #@UndefinedVariable
            raise ExitingException("Could not ReadProcessMemory: ", windll.kernel32.GetLastError()) #@UndefinedVariable
    
    def _RPM_int(self, process_handle, address):
        buf_int = c_int()
        self._RPM(process_handle, address, buf_int)
        return buf_int.value
    
    def _get_int_in_raw(self, raw, addr):
        return unpack("i", raw[addr-PATTERN_START_ADDR:addr-PATTERN_START_ADDR+4])[0]
    
    def _get_byte_in_raw(self, raw, addr):
        return unpack("b", raw[addr-PATTERN_START_ADDR:addr-PATTERN_START_ADDR+1])[0]
