This page's purpose is to explain how to customize the settings for the Python Box ESP.

# Introduction #

With the release of External Box ESP in Python, users are now able to edit their hacks in
a easy to read user friendly configuration ("config") file. Here I provide some information
to easily know what features do what and to explain with example config, how to customize Extrenal Box ESP Python port.


# Details #
First things first:
  * config - the file that holds the configuration information is simply a text file without an extension. Open this file up in any text editor. I suggest Notepad2 http://www.flos-freeware.ch/notepad2.html

Now to the editing:

  * The config file from release version 5.0

```

#
# This is the configuration file for ExternalBoxESP+bot by Sph4ck
#
# you should find here many parameters to customize your hack without changing code
#

# this file is interpreted as Python code, so beware: you can easily break the program

# ----------------------------------------------------------------------
# Offsets for COD6 - build 1.1.195
#
```
These are the reference locations in memory  for structures in 1.195 version of CODMW:2
No need to edit this information unless the game updates to a new version and the offsets change.
```
REFDEF = 0x860030
ENTITY = 0x8F8AF8
CLIENTINFO = 0x8EC2C8
CG_T = 0x7F59BC
CGS_T = 0x7F1CF8

ISINGAME = 0x7F58C8
VIEWANGLEY = 0xB36A40
ADDR_KILLS = 0x01B2C918
ADDR_DEATHS = 0x01B2C920
```
Name of the window to the hack searches for when looking for MW:2, do not change this.
```
COD_WINDOW_NAME = "Modern Warfare 2"
```
Used for debugging purposes, do not change unless you know how to script in Python.
```
# ----------------------------------------------------------------------
# MOCK is set to True to debug purposes only
#
MOCK = False              # only used to test hack without the game running
PROFILING = False        # only used for debug profiling

# ----------------------------------------------------------------------
# You can customize below to avoid easily bannable hack
```
Used to change the name of the .EXE file window that launches the hack.
Change this to anything else and it makes it harder to detect.
```
APP_NAME = 'Launcher'			# name of the hack window

# this specifies the pause (sleep) between two iterations
# the number is in seconds, 0.010 meaning 10ms
# normally 0 should be OK but it might eat up too much CPU. 0.010 is also fine and less aggressive
```
Do not change these values unless told to do so, these are for timing between functions and iterations.
```
MAIN_LOOP_SLEEP = 0.0
if PROFILING: MAIN_LOOP_SLEEP = 0.000

# ----------------------------------------------------------------------
# Graphical preferences
#
# All colors are in 0xAARRGGBB format
#	AA = (alpha) transparency, from 00 (transparent) to FF (opaque)
#	RR = red
#	GG = green
#	BB = blue
```
The radar is square, this number changes the size in pixels of the radar squared.
```
# position of the Radar on the screen
RADAR_SIZE = 160            # size of the radar in pixels
RADAR_OFFSET = 20           # margin from top and right of the screen, in pixels
```
These settings allow you to change the Box ESP colors:
these colors are in the 0xAARRGGBB format as stated above.
I suggest you use a tool like Hex Color Finder http://www.tucows.com/preview/240092
This program allows you to easily find a color you like and get the hex value.
  * he color you pick should always be in 0xAARRBBGG format
  * A is alpha - "read transparency/opaque"
  * n hex 00 = 0, FF = 255 (00 is completely transparent and FF is completely opaque)
  * n order to find a alpha level you like, estimate between 0 and 255 what you think you would like your transparency to be (for example "125" 125 is about half way visible) take 125 and use a tool like http://www.easycalculation.com/decimal-converter.php
when you type "125" in decimal you get "7D" in hex, so your alpha value is "7D".
  * RRBBGG is the color format in hex, if you notice when you use "Hex Color Finder", The hex value you get is in #RRBBGG format where "RR" is how much red between 0 and 255 same with "BB" for blue and "gg" for green.
```
# colors for the BOX Esp
COLOR_FRIEND = 0x7F0000FF                  # blue
COLOR_ENEMY = 0x7FC00000                   # dark red
COLOR_ENEMY_COLDBLOODED = 0x80FFBF00       # orange
COLOR_DEAD = 0x7F444444                    # dead body, the player is watching killcam
COLOR_SENTRY = 0x7F00B050                  # green
COLOR_EXPLOSIVE = 0x3F7F7F7F               # yellow

```
Width of the snap line connecting the box ESP to the bottom middle of the screen.
```
# 
COLOR_BOX_LINE_WIDTH = 3					# width of the arrow from lower screen to box
```
This bit should be self explanatory, if not, let me know and I'll add a bit.
```
COLOR_BOX_OUTER_WIDTH = 3					# width of the Box ESP
COLOR_PLAYER_NAME = 0x7FFFFFFF				# color of the player name
PLAYER_NAME_FONT = "Arial"
PLAYER_NAME_SIZE = 14
PLAYER_NAME_WEIGHT = 400

# colors for mini-map
MAP_COLOR_BACK = 0x44000000					# radar back color
MAP_COLOR_BORDER = 0x7F0000FF				# radar border color
MAP_COLOR_ME = 0xFF00FF00					# color of my player
MAP_COLOR_FRIEND = 0xFF4444FF				# color of team-mates
MAP_COLOR_ENEMY = 0XFFFF4444				# color of enemies
MAP_COLOR_ENEMY_COLDBLOODED = 0XFFFFBF44	# color of enemies with coldblood perk

# color of the claymore ESP
COLOR_CLAYMORE = 0x3FFF6666					# color of claymores
COLOR_PLANE = 0x7F880088                    # color for planes & helicopters

# distance ESP (in meters or ft)
```
This number should not change as it is a real number used to convert feet to meters etc.
```
DISTANCE_ESP_UNIT =  0.03048                # use  0.03048 for meters, or 0.1 for ft
```
Here you have the option of displaying Distance a player is in either feet or meters.
```
DISTANCE_ESP_UNIT_NAME = "m"                # either "m" or "ft"
```
This should be self explanatory.
```
# fading esp
FADE_ENABLED = True                         # set to False to disable fading
```
This is the minimum distance at which distance fading will start to fade for esp, (read change transparency)
```
FADE_MIN_DIST = 600                         # in 1/10th of ft, so 600 is ~20m
FADE_MIN_ALPHA = 0x7F                       # level of transparency
```
This is the max distance that a player will fade out, to avoid a player going completely transparent.
```
FADE_MAX_DIST = 2500                        # in 1/10th of ft, 2500 is ~80m
FADE_MAX_ALPHA = 0x3F                       # level of transparency
# ----------------------------------------------------------------------
# rage module - special coloring for the player you want to rage
```
Keys used to cycle through players to mark as a rage target.
```
KEY_RAGE_PREV = "VK_PRIOR"                    # page up
KEY_RAGE_NEXT = "VK_NEXT"                   # page down
```
You know how to set colors! :)
```
RAGE_COLOR_ESP = 0XFFFF0066                 # purple
RAGE_COLOR_MAP = 0XFFFF0066                 # purple

# ----------------------------------------------------------------------
# Cross hair
CROSSHAIR_COLOR = 0xCCFF1111				# crosshair color
```
Width of the crosshair.
```
CROSSHAIR_WIDTH = 2							# crosshair width
```
Length of the line that is rendered in both horizontal and vertical direction.
```
CROSSHAIR_SIZE = 10							# crosshair length

# ----------------------------------------------------------------------
# Status line
STATUS_COLOR_ACTIVE = 0xFFFFCC00
STATUS_COLOR_INACTIVE = 0xFF777777
STATUS_COLOR_LINE = 0xAF000000              # color of status line
KEY_STATUS = "F1"                           # is status display enabled
KEY_STATUS_UP = "F2"                        # to select if you want the status up on the screen

# ----------------------------------------------------------------------
# killstreak display

KILLSTREAK_FONT = "Arial"
KILLSTREAK_SIZE = 120
KILLSTREAK_WEIGHT = 700
# ----------------------------------------------------------------------
# bot constants
```
I suggest that you do not edit this area as they are real numbers used to calculate bot functions. You can seriously mess things up if you don't know what you are doing.
```
GRAV = 322.0                        # in 1/10th of feet/s2
TUBE_VEL = 1550.0                   # which is 155 ft/s, or 47m/s
KNIFE_VEL = 940.0                   # which is 90 ft/s, or 27m/s

# below are the hieght of aiming for regular weapon, depending on pose
# feet-to-eyes are 60 (stand), 40 (crouched), 20 (prone)
# beware that having too much headshots can unbalance your stats, use EAM to reset them
```
This is the location in distance from the foot on up that the aimbot will aim when a player is standing up.
```
BOT_STAND_Z = 48            # or 55 for more headshots
```
This is the location in distance from the foot on up that the aimbot will aim when a player is crouched.
```
BOT_CROUCHED_Z = 38
```
This is the location in distance from the foot on up that the aimbot will aim when a player is prone.
```
BOT_PRONE_Z = 10
```
We aim for the foot when shooting a tube, to avoid over shooting.
```
BOT_TUBE_Z = 0
```
We aim for the mid chest when knifing to avoid missing.
```
BOT_KNIFE_Z = 40
```
This is the number that defines a "search" area for enemies in the center of the screen /squared. 300 will create a search area of 300 by 300 pixels from the center of the screen to search for esp box of a enemy. To be less obvious I suggest you make it somthing like "40". Up to you however.
```
BOT_MIN_PIX_TO_CENTER = 300         # aim only if not more than 300 pixels from center of screen
```
The closest enemy to you has a tiny circle drawn over the middle of them, this is the color for that spot.
```
BOT_FRAME_COLOR = 0x3FFFFFFF        # color of the spot
```
The speed of the bot in regular use, 5 - 7 good numbers 2 is for sniper use, or effect of External Box ESP v4.32
```
BOT_SPEED_1 = 5
```
Tick is how long a player has been tracked in the search area of the aimbot, the longer you have followed a player with your sights the more aggressive the bot gets.
```
BOT_SPEED_TICK_1 = 15
BOT_SPEED_2 = 3
BOT_SPEED_TICK_2 = 30
BOT_SPEED_3 = 2
# ----------------------------------------------------------------------
```
Defines the default state of each key Fx, when the hack starts up True means "ON" False means "OFF"
```
# Fx keys default values, select if Fx is enabled or disabled by default
F1 = False
F2 = False
F3 = True
F4 = True
F5 = True
F6 = True
F7 = False
F8 = True
F9 = False
F10 = True
F11 = True
F12 = True
```
The name displayed on the hack, describing what each button controls.
```
# labels
F1_LABEL = ""
F2_LABEL = ""
F3_LABEL = "crosshair"
F4_LABEL = "explosives"
F5_LABEL = "aimbot"
F6_LABEL = "tubebot"
F7_LABEL = "knifebot"
F8_LABEL = "autostab"
F9_LABEL = "triggerbot"
F10_LABEL = "radar"
F11_LABEL = "boxesp"
F12_LABEL = "snapline"

# virtual keys ON and OFF are also accepted if always on or off
# all globs starting with IS_ are parsed and mapped to an F key or ON/OFF
```
Here is where you can change the toggles for the keys that turn features on and off.
```
KEY_CROSSHAIR =     "F3"
KEY_EXPLOSIVES =    "F4"
KEY_AIMBOT_ACTIVE =        "F5"
KEY_TUBEBOT_ACTIVE =       "F6"
KEY_KNIFEBOT_ACTIVE =      "F7"
KEY_AUTOSTAB =      "F8"
KEY_TRIGGERBOT =    "F9"
KEY_RADAR =         "F10"
KEY_BOXESP =        "F11"
KEY_BOX_SNAPLINE =   "F12"

# all globals beginning with KEY_ are parsed and corresponding keys are being scannec
# key codes can be Windows VK_* key codes or single characters
# seperate multiple keys with spaces
```
Key binds for the following keys may be changed. You only need change the portion between the '" "' You can use a list of Virtual Key's http://msdn.microsoft.com/en-us/library/ms927178.aspx
or you can use real keys, such as 'T', 'M' etc.
```
KEY_BOT = "VK_RBUTTON"
KEY_TUBEBOT = "VK_HOME VK_MBUTTON"
KEY_KNIFEBOT = "G VK_MBUTTON"
KEY_INDIRECT_BOT = "VK_CAPITAL"         # CAPS LOCK

TRIGGER_BOT_FIRE_KEY = ord("H")         # key triggered when using triggerbot
# ----------------------------------------------------------------------
# autostab parameters
```
Distance at which the autostab bot will start to stab and enemy.
```
AUTOSTAB_DIST = 150             # distance in 1/10th of ft
AUTOSTAB_DIST_Z = 50            # max vertical distance (otherwise you try to stab people above/under you)

# ----------------------------------------------------------------------
# killstreak counter
```
Turn killsteak counter "ON" "OFF"
```
KEY_KILLSTREAK = "ON"           # always on
KILLSTREAK_FONT_NAME = "Arial"
KILLSTREAK_FONT_SIZE = 120
KILLSTREAK_FONT_WEIGHT = 700    # bold
KILLSTREAK_FONT_COLOR = 0x5FFFFFFF  # grey

# ----------------------------------------------------------------------
```
Here you should set whether or not you would like the hack to work with inverted mouse settings.
```
# Mouse inversion option: Mouse settings inverted = True; Mouse settings normal = False;
MOUSE_INVERSION = False

# ----------------------------------------------------------------------
```
Used for debug purposes, no need to edit.
```
# inspector class for debug
KEY_INSPECTOR = "VK_NUMPAD0"

```