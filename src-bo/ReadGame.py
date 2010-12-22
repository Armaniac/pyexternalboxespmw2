import re
from ctypes import windll
from time import sleep
from structs import *   #@UnusedWildImport
from Config import *    #@UnusedWildImport
from utils import ExitingException

# game_modes
# dm= Free for all
# sab= Sabotage
# war= Team Death Match
# dom= Domination
# dd= Demolition
# koth= HQ
# sd= Search & Destroy
# ctf= Catch the flag

class ReadGame(object):
    
    def __init__(self, env):
        self.env = env
        
        # global info
        self.is_inited = False
        self.is_in_game = False
        
        # window and frame info
        self.cod7_hwnd = 0               # handle of overlay window
        self.cod7_pid = 0                # process id of COD6
        self.cod7_process = None         # process handle of COD6
        self.resolution_x = 0           # game window resolution
        self.resolution_y = 0           
        self.screen_center_x = self.resolution_x / 2    # game window center
        self.screen_center_y = self.resolution_y / 2  
        self.mouse_center_x = 0         # mouse center
        self.mouse_center_y = 0
        self.wnd_bounding_x = 0         # game bounding box origin
        self.wnd_bounding_y = 0
        
        # objects read from game memory
        self.local_client_num = 0
        self.deaths = 0 
        self.kills = 0
        self.cod7_refdef = COD7_RefDef()
        self.cod7_clientinfo = COD7_ClientInfo()
        self.cod7_entity = COD7_Entity()
        self.cg = COD7_CG_T();
        self.cgs = COD7_CGS_T();
        self.map_name = None
        self.map_name_re = re.compile("/(mp_\w+)\.d3dbsp")
        self.game_time = 0
        self.game_mode = ""
        self.is_host_text = ""
        self.sensitivity_raw = 5.0      # in-game mouse sensitivity
        self.sensitivity = 5.0          # in-game mouse sensitivity
        #These are internal variables to determine if we are new in round, leaving round, or mapname
        self.maps_temp = None
        self.round_start = False
        self.round_end = False

        # pre-mashed info
        self.fov_x = 0.0                # field of view
        self.fov_y = 0.0
        self.killstreak = -1            # current killstreak number
        self.local_client_num = 0
        self.my_team = 0                # my team number
        self.my_pos = VECTOR()          # my position vector
        self.view_angles = VECTOR()
        self.view_axis = [ VECTOR(), VECTOR(), VECTOR() ]
        
        self.player = [Player() for i in range(PLAYERMAX)] #@UnusedVariable
        self.tracked_ent = {}
        self.my_player = self.player[0]
        
        # internal private
        self._last_deaths = 0 
        self._last_kills = 0
        
        # used for motion vector calculation
        self._last_game_time = 0
        self._last_pos3 = [ VECTOR(0,0,0) for x in range(PLAYERMAX) ] #@UnusedVariable
    
    def init(self):
        print "External Hack version 1.0 by sph4ck"
        print "for COD7 BlackOps"
        print "- works on Vista/Win7 with Aero theme activated"
        print
        print "Waiting for BlackOps game..."
        while self.cod7_hwnd == 0:
            if not DEBUG:
                self.cod7_hwnd = windll.user32.FindWindowA(COD_WINDOW_CLASS, None)
            else:
                self.cod7_hwnd = windll.user32.FindWindowA(None, "Microsoft Office Communicator")
            sleep(0.050)
        print "COD7 game found."
        while self.cod7_pid == 0:
            hwnd = c_int()
            tid = windll.user32.GetWindowThreadProcessId(self.cod7_hwnd, byref(hwnd)) #@UnusedVariable
            self.cod7_pid = hwnd.value
            sleep(0.050)
        print "Found process ID: ", self.cod7_pid
        
        # boost our own process priority
        own_process = windll.kernel32.GetCurrentProcess() #@UndefinedVariable
        windll.kernel32.SetPriorityClass(own_process, 0x00008000)       # ABOVE_NORMAL_PRIORITY_CLASS @UndefinedVariable
        
        self.cod7_process = windll.kernel32.OpenProcess(0x0010, False, self.cod7_pid)  # 0x0010 = PROCESS_VM_READ @UndefinedVariable
        
        
        client_rect = RECT()
        windll.user32.GetClientRect(self.cod7_hwnd, byref(client_rect))
        self.resolution_x = client_rect.right
        self.resolution_y = client_rect.bottom
        self.screen_center_x = self.resolution_x / 2
        self.screen_center_y = self.resolution_y / 2
        bounding_rect = RECT()
        windll.user32.GetWindowRect(self.cod7_hwnd, byref(bounding_rect))
        self.mouse_center_x = (bounding_rect.right + bounding_rect.left) / 2
        self.mouse_center_y = (bounding_rect.bottom + bounding_rect.top) / 2
        
        # window origin
        pt = POINT(0, 0)
        windll.user32.ClientToScreen(self.cod7_hwnd, byref(pt))
        self.wnd_bounding_x = pt.x
        self.wnd_bounding_y = pt.y

        print "Resolution: %d x %d, pos: %ix%ix%ix%i" % \
            (self.resolution_x, self.resolution_y,
             bounding_rect.left, bounding_rect.top, bounding_rect.right, bounding_rect.bottom)
        self.is_inited = True
    
    def check_window_moved(self):
        bounding_rect = RECT()
        if not windll.user32.GetWindowRect(self.cod7_hwnd, byref(bounding_rect)):
            raise ExitingException("Could not ClientToScreen: ", windll.kernel32.GetLastError()) #@UndefinedVariable
        new_mouse_center_x = (bounding_rect.right + bounding_rect.left) / 2
        new_mouse_center_y = (bounding_rect.bottom + bounding_rect.top) / 2
        if self.mouse_center_x != new_mouse_center_x or self.mouse_center_y != new_mouse_center_y:
            self.mouse_center_x = new_mouse_center_x
            self.mouse_center_y = new_mouse_center_y
            pt = POINT(0, 0)
            if not windll.user32.ClientToScreen(self.cod7_hwnd, byref(pt)):
                raise ExitingException("Could not ClientToScreen: ", windll.kernel32.GetLastError()) #@UndefinedVariable
            self.wnd_bounding_x = pt.x
            self.wnd_bounding_y = pt.y
            return True
        elif self.cod7_hwnd == 0:
            return False
        return False
        
    
    def _RPM(self, address, buffer):
        if not windll.kernel32.ReadProcessMemory(self.cod7_process, address, byref(buffer), sizeof(buffer), None): #@UndefinedVariable
            raise ExitingException("Could not ReadProcessMemory: ", windll.kernel32.GetLastError()) #@UndefinedVariable

    def _RPM_int(self, address):
        buf_int = c_int()
        self._RPM(address, buf_int)
        return buf_int.value
    
    def _RPM_float(self, address):
        buf_float = c_float()
        self._RPM(address, buf_float)
        return buf_float.value
        
    def render(self):
        self._RPM(CG_T, self.cg)
        self.game_time = self.cg.time
        self.is_in_game = (self.game_time != 0 )
        self.local_client_num = self.cg.clientNum
        
        if self.is_in_game and self.local_client_num >= 0 and self.local_client_num < PLAYERMAX:
            #===================================================================
            self.kills = self.cod7_clientinfo.arr[self.local_client_num].kills
            self.deaths = self.cod7_clientinfo.arr[self.local_client_num].deaths
            self._RPM(CGS_T, self.cgs)
            #===================================================================
        
            self._RPM(REFDEF - 0x158, self.cod7_refdef)
            self._RPM(ENTITY, self.cod7_entity)
            self._RPM(CLIENTINFO, self.cod7_clientinfo)
            self.calc_killstreak()
            
            # sensitivity
            # It gives in-game mouse sensitivity.
            # It is a float from 1.0 (low sensitivity) to 30.0. Default is 5.0
            sensitivity_ptr = self._RPM_int(SENSITIVITY_DVAR) + 24
            self.sensitivity_raw = self._RPM_float(sensitivity_ptr)
            #self.sensitivity_raw = self._RPM_float(SENSITIVITY_PTR)
            self.sensitivity = self.sensitivity_raw
            if self.sensitivity < 1.0 or self.sensitivity > 30.0:
                self.sensitivity = 5.0
                self.sensitivity_raw = -1
            # map name location currently in use, needs formating with regexp to be proper match for our needs.
            self.map_name = self.cgs.map
            match = self.map_name_re.search(self.map_name)
            if match:
                self.map_name = match.group(1)
            self.game_mode = self.cgs.gamemode
            
            
            # views
            self.fov_x = self.cod7_refdef.fov_x
            self.fov_y = self.cod7_refdef.fov_y
            self.my_pos = self.cod7_refdef.viewOrg
            #self.my_pos = self.cg.lerpOrigin
            #self.my_pos.z += 60
            self.view_axis = self.cod7_refdef.viewAxis
            #self.view_angles = self.cod7_refdef.viewAngles
            self.view_angles.x = self.cg.viewAngleY
            self.view_angles.y = self.cg.viewAngleX
            self.view_angles.z = 0
            
            # copy entities and cient_info
            for i in range(PLAYERMAX):
                self.player[i].set_values(self.cod7_entity.arr[i], self.cod7_clientinfo.arr[i])
            
            self.my_player = self.player[self.local_client_num]
            self.my_team = self.my_player.team
            
            # calculate colors
            for p in self.player:
                p.color_esp = COLOR_ENEMY
                p.color_map = MAP_COLOR_ENEMY
                if (p.type == ET_PLAYER) and p.valid and p.alive:
                    if ((p.team == 1 or p.team == 2) and (p.team == self.my_team)) or p == self.my_player:
                        p.enemy = False
                        if p.alive & ALIVE_FLAG:
                            p.color_esp = COLOR_FRIEND
                            p.color_map = MAP_COLOR_FRIEND
                        else:
                            p.color_esp = COLOR_DEAD
                    else:
                        p.enemy = True
                        if p.alive & ALIVE_FLAG:
                            if p.perk & PERK_STEALTH:
                                p.color_esp = COLOR_ENEMY_COLDBLOODED
                                p.color_map = MAP_COLOR_ENEMY_COLDBLOODED
                            else:
                                p.color_esp = COLOR_ENEMY
                                p.color_map = MAP_COLOR_ENEMY
                        else:
                            p.color_esp = COLOR_DEAD
                else:
                    #p.enemy = False        # do not change status and keep old one
                    p.color_esp = COLOR_DEAD
                    
            self.my_player.color_esp = 0
            self.my_player.color_map = MAP_COLOR_ME
            # calculate motion vector
            #===================================================================
            # if self.game_time > self._last_game_time:
            #    k = 1000.0 / (self.game_time - self._last_game_time)
            #    for idx in range(PLAYERMAX):
            #        pos3 = self.player[idx].pos3
            #        last_pos3 = self._last_pos3[idx]
            #        if self._last_game_time > 0:
            #            self.player[idx].motion = VECTOR((pos3.x - last_pos3.x) * k,
            #                                             (pos3.y - last_pos3.y) * k,
            #                                             (pos3.z - last_pos3.z) * k)
            #        last_pos3.x = pos3.x
            #        last_pos3.y = pos3.y
            #        last_pos3.z = pos3.z
            #===================================================================
            #self._last_game_time = self.game_time
        else:           # not is_in_game
            self.tracked_ent.clear()            # clear all tracked entities
            self._last_game_time = 0
            for p in self._last_pos3:
                p.x = p.y = p.z = 0.0
            

    def calc_killstreak(self):
        if not self.is_in_game:                         # invalidate killstreak counter
            self.killstreak = -1                        # negative means uninitialized killstreak counter
            self._last_deaths = self._last_kills = 0
            return
        
        if self.killstreak >= 0:                        # it's up and counting
            if self.deaths != self._last_deaths:
                self._last_deaths = self.deaths
                self._last_kills = self.kills
            self.killstreak = self.kills - self._last_kills
        elif self.kills == 0 and self.deaths == 0:      # game just begun with 0-0 score, start counting
            self.killstreak = 0
        
    #===========================================================================
    # def get_owner_team(self, clientnum):
    #    owner = self.mw2_entity.arr[clientnum].owner
    #    if owner >= 0 and owner < PLAYERMAX:
    #        #print "clientnum=%i, owner=%i, team=%i" % (clientnum, owner, self.mw2_clientinfo.arr[owner].team)
    #        #print dump_obj(self.mw2_entity.arr[clientnum])
    #        return self.mw2_clientinfo.arr[owner].team
    #===========================================================================
        
    def world_to_screen(self, location):
        # return (x,y) or None if non visible
        pos = location - self.my_pos
        transform = VECTOR()
        transform.x = pos.dotProduct(self.view_axis[1])
        transform.y = pos.dotProduct(self.view_axis[2])
        transform.z = pos.dotProduct(self.view_axis[0])
        
        if transform.z < 0.1:
            return None
        
        x = self.screen_center_x * (1 - (transform.x / self.fov_x / transform.z))
        y = self.screen_center_y * (1 - (transform.y / self.fov_y / transform.z))
        return COORD(x, y)
