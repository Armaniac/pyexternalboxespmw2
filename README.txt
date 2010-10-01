External BoxESP v5.2 for Call of Duty 6 - by sph4ck & dheir
Offsets for 1.2.208

*** If you like it, feel free to donate***: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=7AD4BSF3H4KKS

As always ***FULL SOURCE CODE AVAILABLE*** here: http://code.google.com/p/pyexternalboxespmw2/source/checkout


Before asking any questions, read these:
*** THIS HACK IS UNDETECTED: YOU WILL NOT BAN FROM STEAM WITH THIS HACK!
*** THIS HACK DOES NOT WORK ON WINDOWS XP
*** THIS HACK REQUIRES AERO MODE ACTIVE ON VISTA/WIN7
*** THIS HACK REQUIRES WINDOWED GAME MODE, NO FULLSCREEN
*** THIS HACK DOES NOT AND WILL NOT WORK FOR ALTERIW


New features in version 5.2
===========================
- Radar: rotating map in background + show airplanes and hellis + shows airdrop flares
- Bot is now independant of in-game sensitivity
- anti-lag feature: the hack is now in a separate thead and doesn't depend on the Windows event pump
Bug corrections:
- killstreak counter
- BigRadar turned ON by default
- removed knife glitch (didn't work very well)
- removed TK bot (nobody uses it)
- better error reporting when Aero is missing
- corrected estate map where arrows where inverted on radar

Known limitations and bugs:
- friend/enemy indicator on claymore not 100% accurate
- 

New features in version 5.1
===========================
- BigRadar feature: (press NUMPAD +) shows a complete radar map with player. The map does not rotate so that you can do precise airstrikes knowing where players are exactly
- Enhanced explosives ESP: now draw icons to recognize the type of explosive: semtex, grenade, C4, knife, claymore... Claymore are now red/green depending on their teams
- Airdrop ESP: shows where players are sending airdrops flares - ideal for care package stealing
- Automatic tubebot: now aimbot automatically chooses between normal aimbot or tubebot depending on active weapon
- Web statistics: hack sends anonymous stats about the active feature, the game type, map name and your score. This is only for hack improvment in the future.
  *** we never collect your steam id nor XUID nor name nor whatever personal information ***
- Recalibrated gravity and velocity for tubebot and knifebot
- Updated with all DLC packs: Stimulus & Resurgence maps
- Weapon ESP (F6) shows you what weapons other players are using
- all source code now on Google Code Page: http://code.google.com/p/pyexternalboxespmw2/
  *** we do not include source code anymore in the distributed package ***
  If you want source code please download it from Google Code Page

This version is a complete rewrite in Python language. What it means for you is that you don't need to compile anything anymore. The hack is packaged in source format and in ready-to-use EXE. The second benefit is that it is more undetectable than ever - no more hex edit required.

The credits go as follows. This hack originally blended from different code snippets and some personal additions, and a major rewrite.
HUGE CREDITS FOR:
- KN4CK3R who made all this possible by publishing the root source code
- Tristan Ward (not cheat related) for the Direct3D and Aero overlay
- Big Dave for the offsets of every new COD6 build, SuprNovaAO for additionnal offsets, S0beit for Radar, xZetera for various pieces of code, Sumol for updates of BoxESP, blambo for dead bodies removal and arrows in radar, cardoow for coldblooded enemies identification, Ghett0 for knifebot & triggerbot, jixz for tubebot & killstreak counter, kolbybrooks for better mem locations, username_in_use for locking aimbot.
- Special thanks for warezdude92 for huge support

* New features:
- Easier than ever to build and use (no more VC++ and DirectX SDK download)
- Easy to customize config file
- Better stealth mode: the EXE contains no hack related features + a memory location scrambler moves data structures randomly
- Box ESP now works for helicopters and planes (no yet for UAV)
- Box ESP no has the snap-line option (lines going from the bottom of the screen to the enemies)
- Box ESP has progressive transparency based on distance
- Rage option to mark a specific enemy you want to kill over and over (PageUP / PageDOWN)
- Status bar now at the bottom of the screen (simpler code)

OK, on to the good stuff. Hopefully this will alleviate a bunch of questions on the forum.

* INFORMATION:
1. You are downloading a hack that was designed for Windows 7/Vista.
The reason this hack is for windows 7/Vista is because it uses functions of Windows AERO to use as a medium to draw the hack information on. Windows XP does not and will not have those functions on it (Sorry).

2. You download one .rar file - when extracted it makes a set of folders containing the released compiled version of the stock hack, and a folder with the source code for the hack itself.

3. Why this hack is safe vs. other hacks that are injected.
When you use a hack that injects its own code into a game, it changes information in the running game in your computers memory.
VAC2 is designed to scan for these changes and flag your account for hacking.
This hack uses RPM (Read Process Memory), and does not insert it's own code into the hack. It simply takes information about enemies, their location, etc, and does some math to calculate the information presented on the screen in the form of the hack. The actual information that is show on the screen is not
drawn on the game window itself, (as that would be easily detected), but rather drawn using functions of Windows Aero theme, on and invisible overlay that sits on top of your game. This is why the game needs to be in windowed mode, in order to allow the overlay to sit on top.

4. This hack is designed for a Steam enabled, MW2 for version 1.2.208 + 1.1.195 and no other version.
The reason that this hack will only work for a legit steam version 1.2.208 + 1.1.195 is that when the game gets updated, (from older versions), the location of different values in memory change, these are called offsets. The same applies for private server versions of the game. These different executable's will have different locations that the hacks uses to call upon to gather information for a useful hack.

5. Will you get banned? If you have used another hack in the last 2 weeks or so, it's hard to tell. Don't come here and complain that you got banned if you did.
You take a risk every time you use a hack. It's your fault and no one else. This is free to you to use as you will, and no guarantee is promised. However the risk of being banned after using this hack and this hack alone, is very low, about 1%, the reason for that number is if you were not using it smartly.
If you draw a bunch of attention to yourself and somehow Mr.s Valve himself is playing, and decides to ban you. Understand that this hack is EXTERNAL, meaning it does not alter memory, or executables. Other people playing steam can not get you banned, period.

6. Do not use VACChaos with this, there is no need, period!!

* INSTRUCTIONS: 
Either pre compiled or self compiled versions need this step.

1. You must first switch your COD game from fullscreen to windowed-mode.
You can either press Alt+Enter in game to switch from fullscreen to windowed-mode, and back.

Or you can change the COD6 configuration file:
Go into your C:\Program Files (x86)\Steam\steamapps\common\call of duty modern warfare 2\players\
Look for a file called config_mp.cfg, open that with notepad.
We want to change a line in that file, change fullscreen to false.
seta r_fullscreen "1"
to
seta r_fullscreen "0"

If you don't have a (x86) folder that's ok, it's for people on 64 bit OS's.

2. Decide if you want to use a stand-alone version on the Python source

 INSTRUCTIONS: Using stand-alone executable.

1. Download the file as attachment on the first post of this page
The file name is "External BoxESP V5.2(1.2.208 compatible).rar"

2. If you do not have winrar installed, download it at, [url=http://www.rarlab.com/]WinRAR archiver, a powerful tool to process RAR and ZIP files[/url],
After you know you have winrar installed extract the .rar file to a location, say your desktop for example.
Inside the folder you have this directory structure.
Look inside the folder and you have 'launcher.exe', this is the hack you will use. (Feel free to move this folder anywhere as long as you keep all the files together.)

Note: there is a 'library.zip' containing the actual code in pre-compiled Python bytecode. This zip file may be marked as corrupt by winrar but it's not! (It's actually a .z file).

*** DO NOT RENAME OR UNZIP THE 'library.zip' FILE ! ***
*** DO NOT INJECT ANY DLL ***

 INSTRUCTIONS: Using the source.

Unpack the rar file as above.
Download and Install ActivePython 2.6.xxx (it's free): http://downloads.activestate.com/ActivePython/releases/2.6.5.12/ActivePython-2.6.5.12-win32-x86.msi

Double-click on 'src/lanucher.py'

3. At this stage you should already have changed your game to use a windows mode instead of fullscreen, you have downloaded a working hack, and are ready to play.

4. Start MW2(Multiplayer), wait until it loads to the main screen.
Double click 'launcher.exe' or 'lancher.py' (see 2.), you are ready to use the hack on a server.

5. Trouble running the hack? Make sure if you have UAC turned on that you run MW2 and Hack as administrator by right-clicking and selecting the option.

* Creating your own stand-alone version.
See the 'BUILD.txt' file

* Customizing your version
There is no GUI and will not be. Please take a look at the 'config' file, there are over 100 of parameters you can customize.

MAKE YOUR HACK UNIQUE:
No more needed. You can still change the 'APP_NAME' value in the config file like this:
APP_NAME = 'my personal app name'

INSTRUCTIONS / HACK USAGE:
F3: Crosshair
	Toggle this on or off for a more precise aim.
F4: Explosive Esp
	Turn this on to see enemy grenades, tubes, claymores, stuns, etc.
F5: Aimbot
	Use this to get a lock on the enemy when they are near your crosshairs.
F6:
F7: Knifebot
	Same as Tubebot. Knifebot is for throwing knife, so you know. Bind equipment to "G" or "Middle Mouse Button"
F8: Autostab
	Self explanatory.
F9: Triggerbot
	Fires when you aim at a target with aimbot using right mouse button. Make sure you bind Fire to ,left mouse and H key!!!!
F10: Radar
	Self explanatory.
F11: Box Esp
	Self explanatory.
F12: Snapline
	Draw lines to easily locate enemy players

* More detailed features:
ESP Features:
 - BoxESP - rectangle + name + distance (in meters or ft)
 - Smooth aimbot (right click and HOME key), you can customize aimbot speed
 - Throwing knife bot ('G' key or middle click)
 - bell curved indirect mode for tubebot/knifebot when CAPSLOCK (really funny)
 - autostab
 - triggerbot with autofire (you must map fire action to 'H' key) - fires when the crosshair is inside the BoxESP
 - explosive ESP (red square on all grenades, including claymores)
 - turret ESP (green box - includes static turrets and sentry guns)
 - killstreak counter
  - flicker-less overlay mode
 - full external hack: no hooking on process for maximum stealth mode
 *** do not use any VAC blocker with this hack ***
