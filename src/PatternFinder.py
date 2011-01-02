from binascii import hexlify, unhexlify
import re
from Config import * #@UnusedWildImport
from ctypes import create_string_buffer, windll, byref, sizeof, addressof
from utils import ExitingException
from struct import unpack

PATTERN_START_ADDR = 0x00401000
PATTERN_LEN = 0x00300000
PATTERN_MATCH = unhexlify('FF')

# looking for cvar NULL ptr exception places
FIND_PATTERNS = { 'cvar':           ("A140954D0680781000740956E85380060083C40457E89A24FDFF8B0D88CF6E0183C404",
                                     "FF00000000FFFFFFFFFFFFFFFF00000000FFFFFFFFFF00000000FFFF00000000FFFFFF"),
                  'RegisterShader': ("8B4424048038007506A100000000C389442404E9",
                                     "FFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFF"),
                  'RegisterTag': ("8B5424048BC2568D70018D9B000000008A0883C00184C9",
                                       "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"),
                  'GetTagInfoForClientNum': ("8B4424040FB70445000000006685C0740F0FBFC069C09C0000000500000000C333C0C3",
                                             "FFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFF"),
                  'GetTagForClientNumInfo': ("518B4C241056578B7C24148D44240B505157C6442417FEE8",
                                             "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"),
                  'CG_Trace': ("8B4424188B4C24148B542408568B742414578B7C24146A006A00508B442418515250E8299E0A0083C4185F5EC3",
                               "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFF"),
                  # now variables
                  'cg_time': ("680000000052E8000000006800000000E80000000083C4108AD0EB",
                              "FF00000000FFFF00000000FF000000FFFF00000000FFFFFFFFFFFF"),
                  'ps_clientNum': ("A10000000069C02C050000050000000083EC60833800",
                                   "FF000000FFFFFFFFFFFFFFFF000000FFFFFFFFFFFFFF"),
                  'refdef': ("8B54241C8BF083C4048D4C2408B800000000E800000000D9EE",
                             "FFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FF00000000FFFF"),
                  'dvars': ("8D3480C1E60481C6000000008934850000000083C001F744241800010000A3000000008A442414",
                            "FFFFFFFFFFFFFFFF00000000FFFFFF00000000FFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFF"),
                  'cg_entities': ("6A0057E80000000069F6040200008B44241C81C60000000083C4083B86F8010000",
                                  "FFFFFFFF00000000FFFF0000FFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFFFF"),
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
    
    def _get_int_in_raw(self, raw, addr):
        return unpack("i", raw[addr-PATTERN_START_ADDR:addr-PATTERN_START_ADDR+4])[0]
    
    def _get_byte_in_raw(self, raw, addr):
        return unpack("b", raw[addr-PATTERN_START_ADDR:addr-PATTERN_START_ADDR+1])[0]
