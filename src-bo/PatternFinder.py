from binascii import unhexlify
import re
from Config import * #@UnusedWildImport
from ctypes import create_string_buffer, windll, byref, sizeof, c_int
from utils import ExitingException
from struct import unpack
import time

PATTERN_START_ADDR = 0x00401000
PATTERN_LEN = 0x00700000
PATTERN_MATCH = unhexlify('FF')

WEAPON_PTR         = 0x00c5E218
REFDEF             = 0x2B3DAFC0
CLIENTINFO         = 0x2B3F70E8 
ENTITY             = 0x2B4840DC 
CG_T               = 0x2B398100 #- 2BB97D80 2B
CGS_T              = 0x2B409700 #- 2BC09700
SENSITIVITY_DVAR   = 0x00E3CC54

DOG_T              = 0x00C76038
RXCD_T             = 0x00C75E78
HELI_T             = 0x00C76AB8
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
                  #'sensitivity':                 ("A100000000D9542404D94218D8C9D84018D80D",
                  #                                "FF00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFF"),
                  'weapons':                     ("8B5424048B0D0000000033C08D6424003B1485000000007407403BC176F233C0C3",
                                                  "FFFFFFFFFFFF00000000FFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFFFFFF"),
                  #'cg_t':                        ("8B4424088B0D0000000089818C150700C3",
                  #                                "FFFFFFFFFFFF00000000FFFFFFFFFFFFFF"),
                  'cg_t':                        ("8B4424088B0D000000008b5424045081",
                                                  "FFFFFFFFFFFF00000000FFFFFFFFFFFF"),
                  'cgs_t':                       ("8B4424088B0D0000000083EC24568BB481",
                                                  "FFFFFFFFFFFF00000000FFFFFFFFFFFFFF"),
                  'entities':                    ("8B4424083D000400008B4C24047C198B1500000000C1E10903C8",
                                                  "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFF"),
                  'helis':                       ("68800900006A006800000000E80000000068000600006A0068",
                                                  "FFFFFFFFFFFFFFFF00000000FF00000000FFFFFFFFFFFFFFFF"),
                }

SENSITIVITY_DVAR_PATTERN = "6800000000E800000000D9050000000083C41868000000006A0183EC0CD95C2408A300000000"
SENSITIVITY_DVAR_MASK    = "FFFFFFFFFFFF00000000FFFF00000000FFFFFFFF00000000FFFFFFFFFFFFFFFFFFFF00000000"

class PatternFinder(object):
    
    def __init__(self, env):
        self.env = env
        self.addr = {}
        self.WEAPON_PTR         = None
        self.REFDEF             = None
        self.CLIENTINFO         = None 
        self.ENTITY             = None 
        self.CG_T               = None 
        self.CGS_T              = None
        self.SENSITIVITY_DVAR   = None
        self.DOG_T              = None
        self.RXCD_T             = None
        self.HELI_T             = None

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
        
        ok = False
        while not ok:
            cg_t_ptr = self._get_int_in_raw(raw, self.addr["cg_t"] + 6)
            self.CG_T = self._RPM_int(process_handle, cg_t_ptr)
            print "Found CG_T ptr 0x%x and 0x%x, should be 0x%x" % (cg_t_ptr, self.CG_T, CG_T)
            self.REFDEF = self.CG_T + 0x43100
            print "Calculated REFDEF 0x%x, should be 0x%x" % (self.REFDEF, REFDEF)
            
            cgs_t_ptr = self._get_int_in_raw(raw, self.addr["cgs_t"] + 6)
            self.CGS_T = self._RPM_int(process_handle, cgs_t_ptr)
            print "Found CGS_T ptr 0x%x and 0x%x, should be 0x%x" % (cgs_t_ptr, self.CGS_T, CGS_T)
            
            entities_ptr = self._get_int_in_raw(raw, self.addr["entities"] + 49)
            self.ENTITY = self._RPM_int(process_handle, entities_ptr)
            print "Found ENTITIES ptr 0x%x and 0x%x, should be 0x%x" % (entities_ptr, self.ENTITY, ENTITY)
            self.CLIENTINFO = self.CG_T + 0x5F228
            print "Calculated CLIENTINFO 0x%x, should be 0x%x" % (self.CLIENTINFO, CLIENTINFO)
            
            if self.CG_T == 0 or self.CGS_T == 0 or self.ENTITY == 0:
                print "Game not completely loaded, waiting for 2 seconds"
                print "----------------------------------------"
                time.sleep(2.0)
                continue
            
            self.SENSITIVITY_DVAR = 5.0
#            self.SENSITIVITY_DVAR = self._get_int_in_raw(raw, self.addr["sensitivity"] + 1)
#            print "Sensitivity DVAR found 0x%x, should be 0x%x" % (self.SENSITIVITY_DVAR, SENSITIVITY_DVAR)
            
            self.WEAPON_PTR = self._get_int_in_raw(raw, self.addr["weapons"] + 19)
            print "Found Weapons 0x%x, should be 0x%x" % (self.WEAPON_PTR, WEAPON_PTR)

            self.DOG_T = self._get_int_in_raw(raw, self.addr["helis"] + 59)
            print "Found DOG_T 0x%x, should be 0x%x" % (self.DOG_T, DOG_T)
            self.RXCD_T = self._get_int_in_raw(raw, self.addr["helis"] + 42)
            print "Found RXCD_T 0x%x, should be 0x%x" % (self.RXCD_T, RXCD_T)
            self.HELI_T = self._get_int_in_raw(raw, self.addr["helis"] + 110)
            print "Found HELI_T 0x%x, should be 0x%x" % (self.HELI_T, HELI_T)
            
        
            print "===> All offsets seem ok."
            print "----------------------------------------"
            ok = True
            
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
