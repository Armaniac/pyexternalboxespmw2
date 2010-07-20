from ctypes import windll, Structure, c_byte, byref, WinError
import win32con
import Config
import array

#
# beware this code is auto-adaptative to config, so full of black magic
#
# Special behaviour for Fx keys:
#    VK_F1 -> VK_F12 stores the instant position of keys
#    F1 -> F12 stores the toggled values (initialized from Config default state)

KEY_PRESSED = 0x01          # mask
KEY_TOGGLE = 0x80
KEY_WINDOWS_MASK = KEY_PRESSED | KEY_TOGGLE         # mask to the windows native bits, to avoid unwanted interference
KEY_NEWLY_PRESSED = 0x02    # custom bit (not in Windows) saying we just pressed the key

# ======================================================================
# global init
# VARS
def create_keys_array():
    arr = array.array("B", [0 for i in range(256+2)])  # array of 256+2 unsigned char @UnusedVariable
    arr[-1] = KEY_PRESSED | KEY_TOGGLE  # -1 or 257 is "ON" so activate flags
    return arr                          # -2 or 256 is "OFF" so leave it zero

keys = {}                               # state of toggles
keys_raw = create_keys_array()          # raw state of each key for the current iteration
_prev_keyb = create_keys_array()        # raw state of each key in the last tick (to calculate changes)
_keys_to_read = create_keys_array()     # keys and masks to read (to avoid reading all keys)
_toggle_state = create_keys_array() # contains the XOR values needed to satisfy default values of toggles
_key_globs = {}                         # hash from logical key (ex: aimbot) to virtual key (ex: VK_RBUTTON)
_key_mapping = {}                       # from game virtal key to tuple (code, mask)

# ======================================================================
# mapping of Windows keyboard API
class KEYBOARD_STATE(Structure):
    _fields_ =  [("key", c_byte * 256)]
    
    def get_key(self, idx):
        if idx >= 0:
            return self.key[idx]
        elif idx == -1:
            return KEY_PRESSED | KEY_TOGGLE         # "ON" value
        else:
            return 0                                # "OFF" value

def GetAsyncKeyState(key):
    return (windll.User32.GetAsyncKeyState(key) & 0x8000) != 0

def GetKeyStateToggle(key):
    return (windll.User32.GetKeyState(key) & 0x0001) != 0

def GetKeyboardState():
    keyb = KEYBOARD_STATE()
    if not windll.User32.GetKeyboardState(byref(keyb)):
        raise WinError()
    return keyb

def SetKeyboardState(keyb):
    if not windll.User32.SetKeyboardState(byref(keyb)):
        raise WinError()

    
# ======================================================================
# simple function that takes a tuple of tuple and flatten all elements as a 0-depth tuple
def _flatten(root):
    if isinstance(root, (list, tuple)):
        for element in root:
            for e in _flatten(element):
                yield e
    else:
        yield root

# ======================================================================

def render():
    global _prev_keyb, keys_raw
    _prev_keyb = keys_raw[:]            # deep copy
    read_keys_raw()
    #
    for (gk, l) in _key_mapping.items():
        keys[gk] = any((keys_raw[k] & mask) for (k,mask) in l)

def keyname_to_mask(key_name):
    mask = KEY_PRESSED                          # default is no toggles
    if key_name[0] in ("+", "-", "~", "!"):
        if key_name[0] in ("+", "-", "~"):
            mask = KEY_TOGGLE
        elif key_name[0] == "!":
            mask = KEY_NEWLY_PRESSED
        key_name = key_name[1:]
    if key_name.startswith("VK_"):
        code = getattr(win32con, key_name)
    elif len(key_name) == 1:
        code = ord(key_name)
    elif key_name == "ON":
        code = -1
    elif key_name == "OFF":
        code = -2
    else:
        raise Exception("Unknown key_name: %s" % key_name)
    return (code, mask)

def read_keys_raw():
    for i in range(256):
        keys_raw[i] = 0
        if _keys_to_read[i]:
            keys_raw[i] |= _prev_keyb[i] & KEY_TOGGLE           # copy state of toggle
            keys_raw[i] |= GetAsyncKeyState(i) and KEY_PRESSED  # add key_press bit
            if (keys_raw[i] & KEY_PRESSED) and not (_prev_keyb[i] & KEY_PRESSED):
                keys_raw[i] |= KEY_NEWLY_PRESSED                # set the newly pressed bit
                keys_raw[i] ^= KEY_TOGGLE                       # and invert the toggle bit
    keys_raw[-1] = KEY_TOGGLE | KEY_PRESSED                     # "ON" key

# parse all globals starting with "KEY_" to see what keys we need to read
_key_globs = dict([(k,getattr(Config, k).rsplit()) for k in dir(Config) if k.startswith('KEY_')])
# now parse default toggle values, and configure inverters
for (vk,l) in _key_globs.items():
    _key_mapping[vk] = [keyname_to_mask(n) for n in l]
    for k in l:
        (code, mask) = keyname_to_mask(k)
        _keys_to_read[code] |= mask

read_keys_raw()         # first read to see what are the values of toggles

for k in list(_flatten(_key_globs.values())):
    if k[0] in ("+", "-", "~"):
        (code, mask) = keyname_to_mask(k)
        if k[0] == "+":
            keys_raw[code] |= KEY_TOGGLE
        elif k[0] == "~":
            _toggle_state[code] |= GetKeyStateToggle(code) and KEY_TOGGLE

del _key_globs

render()