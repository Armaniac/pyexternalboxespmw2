from binascii import unhexlify
import re
from Config import * #@UnusedWildImport
from ctypes import create_string_buffer, windll, byref, sizeof, addressof
from utils import ExitingException
from struct import unpack
import win32api

PATTERN_START_ADDR = 0x00401000
PATTERN_LEN = 0x00300000
PATTERN_MATCH = unhexlify('FF')

FIND_PATTERNS = { 
                  'CG_ClientFrame':             ("83ec3453555657e800000000",
                                                 "FFFFFFFFFFFFFFFF00000000"),
                  'getWeaponinfo':              ("8b4424048b0c85000000008b4108c3",
                                                 "FFFFFFFFFFFFFF00000000FFFFFFFF"),
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
            raise ExitingException("Could not ReadProcessMemory: ", win32api.GetLastError())
    
    def _get_int_in_raw(self, raw, addr):
        return unpack("i", raw[addr-PATTERN_START_ADDR:addr-PATTERN_START_ADDR+4])[0]
    
    def _get_byte_in_raw(self, raw, addr):
        return unpack("b", raw[addr-PATTERN_START_ADDR:addr-PATTERN_START_ADDR+1])[0]
