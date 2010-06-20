from ctypes import windll
import win32con
import Config

#
# beware this code is auto-adaptative to config, so full of black magic
#
# Special behaviour for Fx keys:
#    VK_F1 -> VK_F12 stores the instant position of keys
#    F1 -> F12 stores the toggled values (initialized from Config default state)

# VARS
keys = { "ON": True, "OFF": False}      # state of toggles
_f_range = range(1,13)                  # from 1 to 12
_keys_to_read = []
_key_globs = {}

def GetAsyncKeyState(key):
    return (windll.User32.GetAsyncKeyState(key) & 0x8000) != 0

def _flatten(root):
    if isinstance(root, (list, tuple)):
        for element in root:
            for e in _flatten(element):
                yield e
    else:
        yield root
        
def _update_key_variables():
    # now populate the KEY_ globals
    for (g,l) in _key_globs.items():
        key_state = any(keys[k] for k in l)
        keys[g] = key_state

def render():
    # read Fx keys and activate toggles
    for i in _f_range:                                   # from 1 to 12
        state = GetAsyncKeyState(win32con.VK_F1 +i-1)  # current F key state
        prev = keys["VK_F"+str(i)]                     # previous state
        if not prev and state:                              # if pressed and was not pressed before
            keys["F"+str(i)] = not keys["F"+str(i)]     # invert toggle
        keys["VK_F"+str(i)] = state                    # keep previous state
    
    # read all other keys
    for key in _keys_to_read:
        if key.startswith("VK_"): 
            keys[key] = GetAsyncKeyState(getattr(win32con, key))
        elif len(key) == 1:
            keys[key] = GetAsyncKeyState(ord(key))
    _update_key_variables()

# ======================================================================
# global init

for i in _f_range:
    keys["F"+str(i)] = getattr(Config, "F"+str(i))
    keys['VK_F'+str(i)] = False        # store VK_Fx values
            
# parse all globals starting with "KEY_" to see what keys we need to read
_key_globs = dict([(k,getattr(Config, k).rsplit()) for k in dir(Config) if k.startswith('KEY_')])
#_key_globs = dict([(k,v.rsplit()) for (k,v) in globals().items() if k.startswith('KEY_')])
_keys_to_read = list(_flatten(_key_globs.values()))
for k in _keys_to_read:
    keys.setdefault(k, False)

_update_key_variables()
