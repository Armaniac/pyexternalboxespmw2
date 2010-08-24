#
# This is the configuration file for ExternalBoxESP+bot by sph4ck & dheir
#
# you should find here many parameters to customize your hack without changing code
#

# this file is interpreted as Python code, so beware: you can easily break the program

# ----------------------------------------------------------------------
# Offsets for COD6 - build 1.2.208
#
REFDEF = 0x860030
ENTITY = 0x8F8AF8
CLIENTINFO = 0x8EC2C8
CG_T = 0x7F59BC
CGS_T = 0x7F1CF8

ISINGAME = 0x7F58B8
VIEWANGLEY = 0xB36A40
ADDR_KILLS = 0x01B2C918
ADDR_DEATHS = 0x01B2C920
WEAPON_DESC = 0x7E6D08
ADDR_MAPS = 0x008F278 #mpIntro triggers when map start countdown from "5" mpOutro triggers on map end.
GET_HOST_ADDR = 0x00A86758
ADDR_SENSITIVITY_PTR_16 = 0x00A86730

COD_WINDOW_NAME = "Modern Warfare 2"

# ----------------------------------------------------------------------
PROFILING = False        # only used for debug profiling

# ----------------------------------------------------------------------
# You can customize below to avoid easily bannable hack

APP_NAME = 'Launcher'            # name of the hack window

# this is the maximum FPS allowed for the hack. It is not guaranteed that it will reach that level though...
MAIN_MAX_FPS = 50
if PROFILING: MAIN_LOOP_SLEEP = 1000000

# ----------------------------------------------------------------------
# Graphical preferences
#
# All colors are in 0xAARRGGBB format
#    AA = (alpha) transparency, from 00 (transparent) to FF (opaque)
#    RR = red
#    GG = green
#    BB = blue

# position of the Radar on the screen
RADAR_SIZE = 160            # size of the radar in pixels
RADAR_OFFSET = 20           # margin from top and right of the screen, in pixels
RADAR_CENTER_X = 0          # X offset from center: 0 means center of the screen
RADAR_RANGE = 50            # this is the scale divider for the radar: the higher value, the higher range (players are closer)

KEY_BIG_RADAR = "+VK_ADD "  # display a global map with players, good for air-strikes
KEY_RADAR_MAP = "ON"        # display map background?
BIG_RADAR_SCALE = 0.5       # scale factor for maps, 1.0 makes a 512x512 pix, 0.5 is reduced to 256x256
BIG_RADAR_BLENDING = 0xAF7F7F7F     # blending color used in BigRadar

# colors for the BOX Esp
COLOR_FRIEND = 0x7F0000FF                  # blue
COLOR_ENEMY = 0x7FC00000                   # dark red
COLOR_ENEMY_COLDBLOODED = 0x80FFBF00       # orange
COLOR_DEAD = 0x7F444444                    # dead body, the player is watching killcam
COLOR_SENTRY = 0x7F00B050                  # green
COLOR_EXPLOSIVE = 0x3F7F7F7F               # yellow

# 
COLOR_BOX_LINE_WIDTH = 3                    # width of the arrow from lower screen to box
COLOR_BOX_OUTER_WIDTH = 3                   # width of the Box ESP
COLOR_PLAYER_NAME = 0x7FFFFFFF              # color of the player name
PLAYER_NAME_FONT = "Arial"
PLAYER_NAME_SIZE = 14
PLAYER_NAME_WEIGHT = 400

# colors for mini-map
MAP_COLOR_BACK = 0x44000000                 # radar back color
MAP_COLOR_BORDER = 0x7F0000FF               # radar border color
MAP_COLOR_ME = 0xFF00FF00                   # color of my player
MAP_COLOR_FRIEND = 0xFF4444FF               # color of team-mates
MAP_COLOR_ENEMY = 0XFFFF4444                # color of enemies
MAP_COLOR_ENEMY_COLDBLOODED = 0XFFFFBF44    # color of enemies with coldblood perk

# color of the claymore ESP
COLOR_CLAYMORE = 0x3FFF6666                 # color of claymores
COLOR_CLAYMORE_DISTANCE = 0x7FFF6666        # color of distance indicator for claymore
COLOR_CLAYMORE_SPRITE = 0xAF7F7F7F          # blending color for sprites
COLOR_PLANE = 0x7F880088                    # color for planes & helicopters

COLOR_MAP_BLENDER_FRIEND = 0xFF7FFF7F       # adds green color to friend sprites
COLOR_MAP_BLENDER_ENEMY = 0xFFFF7F7F        # adds red color to enemy sprites

# distance ESP (in meters or ft)
DISTANCE_ESP_UNIT =  0.03048                # use  0.03048 for meters, or 0.1 for ft
DISTANCE_ESP_UNIT_NAME = "m"                # either "m" or "ft"

# fading esp
FADE_ENABLED = True                         # set to False to disable fading
FADE_MIN_DIST = 300                         # in 1/10th of ft, so 600 is ~20m
FADE_MIN_ALPHA = 0xFF                       # level of transparency
FADE_MAX_DIST = 2500                        # in 1/10th of ft, 2500 is ~80m
FADE_MAX_ALPHA = 0x32                       # level of transparency
# ----------------------------------------------------------------------
# rage module - special coloring for the player you want to rage

KEY_RAGE_PREV = "!VK_PRIOR"                 # page up
KEY_RAGE_NEXT = "!VK_NEXT"                  # page down
KEY_RAGE_RESET = "!VK_DELETE"               # delete key

RAGE_COLOR_ESP = 0XFFFF0066                 # purple
RAGE_COLOR_MAP = 0XFFFF0066                 # purple

# below is the display of raged player
KEY_RAGE_DISPLAY_NAME = "VK_PRIOR VK_NEXT VK_DELETE"
RAGE_FONT_NAME = "Arial"
RAGE_FONT_SIZE = 24
RAGE_FONT_WEIGHT = 700
RAGE_FONT_COLOR = 0xBFFFFFFF                # white
RAGE_RESET_STRING = "-------------"

# ----------------------------------------------------------------------
# Cross hair
CROSSHAIR_COLOR = 0xCCFF1111                # crosshair color
CROSSHAIR_WIDTH = 2                         # crosshair width
CROSSHAIR_SIZE = 10                         # crosshair length

# ----------------------------------------------------------------------
# Status line
STATUS_COLOR_ACTIVE = 0xFFFFCC00
STATUS_COLOR_INACTIVE = 0xFF777777
STATUS_COLOR_LINE = 0xAF000000              # color of status line
KEY_HOST_DISPLAY = "ON"

# ----------------------------------------------------------------------
# killstreak display

KILLSTREAK_FONT = "Arial"
KILLSTREAK_SIZE = 120
KILLSTREAK_WEIGHT = 700
# ----------------------------------------------------------------------
# bot constants

GRAV = 800.0
TUBE_VEL = 2400.0
KNIFE_VEL = 1420.0

TUBE_WEAPONS = ("WEAPON_M203", "WEAPON_M79", "WEAPON_GP25")
SNIPER_RIFLES_RE = "^(WEAPON_CHEYTAC|WEAPON_M21|WEAPON_WA2000|WEAPON_BARRETT).*$"

# below are the height of aiming for regular weapon, depending on pose
# feet-to-eyes are 60 (stand), 40 (crouched), 20 (prone)
# beware that having too much headshots can unbalance your stats, use EAM to reset them
BOT_STAND_Z = 48            # or 55 for more headshots
BOT_CROUCHED_Z = 38
BOT_PRONE_Z = 10

BOT_TUBE_Z = 0
BOT_KNIFE_Z = 0

BOT_MIN_PIX_TO_CENTER = 300         # aim only if not more than 300 pixels from center of screen
BOT_FRAME_COLOR = 0x3FFFFFFF        # color of the spot

BOT_SPEED_1 = 5
BOT_SPEED_TICK_1 = 15
BOT_SPEED_2 = 3
BOT_SPEED_TICK_2 = 30
BOT_SPEED_3 = 2
# TK Bot Config Info
TK_BOT_COLOR = 0xFFFF0000
KEY_TK_BOT = "~VK_RMENU" #Key to bind toggle for Aimbot to aim at same team.
# ----------------------------------------------------------------------
# labels
F1_LABEL = "display"
F2_LABEL = "move disp"
F3_LABEL = "crosshair"
F4_LABEL = "explosives"
F5_LABEL = "aimbot"
F6_LABEL = "weapons"
F7_LABEL = "knifebot"
F8_LABEL = "autostab"
F9_LABEL = "triggerbot"
F10_LABEL = "radar"
F11_LABEL = "boxesp"
F12_LABEL = "snapline"

# virtual keys ON and OFF are also accepted if always on or off
# all globs starting with IS_ are parsed and mapped to an F key or ON/OFF
KEY_STATUS =                "+VK_F1"                        # is status display enabled
KEY_STATUS_UP =             "+VK_F2"                        # to select if you want the status up on the screen 
KEY_CROSSHAIR =     		"+VK_F3"
KEY_EXPLOSIVES =    		"+VK_F4"
KEY_AIMBOT_ACTIVE =        	"+VK_F5"
KEY_TUBEBOT_ACTIVE =       	"+VK_F5"                        # same as AIMBOT
KEY_WEAPON_ESP =            "-VK_F6"
KEY_KNIFEBOT_ACTIVE =      	"-VK_F7"
KEY_AUTOSTAB =      		"-VK_F8"
KEY_TRIGGERBOT =    		"-VK_F9"
KEY_RADAR =         		"+VK_F10"
KEY_BOXESP =        		"+VK_F11"
KEY_BOX_SNAPLINE =   		"+VK_F12"

# all globals beginning with KEY_ are parsed and corresponding keys are being scanned
# key codes can be Windows VK_* key codes or single characters
# seperate multiple keys with spaces
KEY_RAPID_KNIFE = "OFF"                  # Used to turn knife glitch on for autostab
KEY_BOT = "VK_RBUTTON VK_HOME"
KEY_TRIGGER_BOT_KEY = "VK_RBUTTON" # Note: this can be same button as KEY_BOT, I just made this available, since I like it :)
KEY_TUBEBOT = "VK_RBUTTON VK_HOME"
KEY_KNIFEBOT = "G VK_MBUTTON"
KEY_INDIRECT_BOT = "~VK_CAPITAL"        # CAPS LOCK
KEY_SNIPER_BOT = "VK_LSHIFT"

TRIGGER_BOT_FIRE_KEY = ord("H")         # key triggered when using triggerbot
KNIFE_RIOT_OFFSET = 2                   # all offsets are considered if RIOT SHIELD is at offset 3
KNIFE_TACTICAL_WEAPONS = (22, 36, 42)   # pistols with tactical knife enabled
# ----------------------------------------------------------------------
# autostab parameters
AUTOSTAB_DIST = 75             # distance in 1/10th of ft
AUTOSTAB_DIST_Z = 50            # max vertical distance (otherwise you try to stab people above/under you)

# ----------------------------------------------------------------------
# killstreak counter
KEY_KILLSTREAK = "ON"           # always on
KILLSTREAK_FONT_NAME = "Arial"
KILLSTREAK_FONT_SIZE = 120
KILLSTREAK_FONT_WEIGHT = 700    # bold
KILLSTREAK_FONT_COLOR = 0x5FFFFFFF  # grey

# ----------------------------------------------------------------------
# Mouse inversion option: Mouse settings inverted = True; Mouse settings normal = False;
MOUSE_INVERSION = False

# ----------------------------------------------------------------------
# airdrop marker persistence
AIRDROP_PERSISTENCE = 15             # number of seconds to keep airdrop marker

# ----------------------------------------------------------------------
# inspector class for debug
KEY_INSPECTOR = "!VK_NUMPAD0"
KEY_INSPECT_POS = "!VK_NUMPAD1"
KEY_INSPECT_DUMP = "!VK_NUMPAD9"
KEY_INSPECT_DUMP_PLAYERS = "!VK_NUMPAD7"

# ----------------------------------------------------------------------
# calibration mode, only used for debugging of tubebot and knifebot
# *** DON'T ACTIVATE UNLESS YOU KNOW WHAT YOU ARE DOING
CALIBRATING = False
KEY_SPOT23_ESP = "OFF"
DEBUG_PRINT_WEAPON_NAMES = False

# ======================================================================
# == CUT HERE to recreate the config file                             ==
# ======================================================================
#
# this is just a wrapper to load globals from the config file, and put them into the Config module symbol table
#
glob_context = {}
local_context = {}
try:
    execfile("config", glob_context, local_context)
    globals().update(local_context)
except Exception as err:
    print "Warning: Could not load 'config' file, reverting to defaults: %s" % err


