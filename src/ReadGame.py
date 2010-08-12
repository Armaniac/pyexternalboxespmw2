import win32api, win32con, win32gui, win32process
import re
from time import sleep
from structs import *   #@UnusedWildImport
from Config import *    #@UnusedWildImport

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
        self.mw2_hwnd = 0               # handle of overlay window
        self.mw2_pid = 0                # process id of COD6
        self.mw2_process = None         # process handle of COD6
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
        self.mw2_refdef = MW2_RefDef()
        self.mw2_mypos = VECTOR()
        self.mw2_viewy = MW2_View_Y()
        self.mw2_clientinfo = MW2_ClientInfo()
        self.mw2_entity = MW2_Entity()
        self.map_name = None
        self.map_name_re = re.compile("/(mp_\w+)\.d3dbsp")
        self.game_time = 0
        self.game_mode = ""
        self.is_host_text = ""
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
        print "External BoxESP+bot version 5.1 by sph4ck & dheir"
        print "for COD6 MW2 - build 1.2.208 & 1.1.195."
        print "- works on Vista/Win7 with Aero theme activated"
        print
        print "Waiting for COD6 game..."
        while self.mw2_hwnd == 0:
            self.mw2_hwnd = win32gui.FindWindow(None, COD_WINDOW_NAME)
            sleep(0.050)
        print "COD6 game found."
        while self.mw2_pid == 0:
            tid, self.mw2_pid = win32process.GetWindowThreadProcessId(self.mw2_hwnd) #@UnusedVariable
            sleep(0.050)
        print "Found process ID: ", self.mw2_pid
        self.mw2_process = win32api.OpenProcess(win32con.PROCESS_VM_READ, False, self.mw2_pid)
        
        client_rect = Rect(win32gui.GetClientRect(self.mw2_hwnd))
        self.resolution_x = client_rect.right
        self.resolution_y = client_rect.bottom
        self.screen_center_x = self.resolution_x / 2
        self.screen_center_y = self.resolution_y / 2
        bounding_rect = Rect(win32gui.GetWindowRect(self.mw2_hwnd))
        self.mouse_center_x = (bounding_rect.right + bounding_rect.left) / 2
        self.mouse_center_y = (bounding_rect.bottom + bounding_rect.top) / 2
        
        # window origin
        pt = (0,0)
        x, y = win32gui.ClientToScreen(self.mw2_hwnd, pt)
        self.wnd_bounding_x = x
        self.wnd_bounding_y = y

        print "Resolution: %d x %d, pos: %ix%ix%ix%i" % \
            (self.resolution_x, self.resolution_y,
             bounding_rect.left, bounding_rect.top, bounding_rect.right, bounding_rect.bottom)
        self.is_inited = True
    
    def check_window_moved(self):
        bounding_rect = Rect(win32gui.GetWindowRect(self.mw2_hwnd))
        new_mouse_center_x = (bounding_rect.right + bounding_rect.left) / 2
        new_mouse_center_y = (bounding_rect.bottom + bounding_rect.top) / 2
        if self.mouse_center_x != new_mouse_center_x or self.mouse_center_y != new_mouse_center_y:
            self.mouse_center_x = new_mouse_center_x
            self.mouse_center_y = new_mouse_center_y
            pt = (0,0)                              # window origin
            x, y = win32gui.ClientToScreen(self.mw2_hwnd, pt)
            self.wnd_bounding_x = x
            self.wnd_bounding_y = y
            return True
        elif self.mw2_hwnd == 0:
            return False
        return False
        
    
    def _RPM(self, address, buffer):
        if not windll.kernel32.ReadProcessMemory(self.mw2_process.handle, address, byref(buffer), sizeof(buffer), None):
            print "Did you close the Modern Warfare 2 window?"
            raise Exception("Could not ReadProcessMemory: ", win32api.GetLastError())

    def _RPM_int(self, address):
        buf_int = c_int()
        self._RPM(address, buf_int)
        return buf_int.value
    
    def _RPM_float(self, address):
        buf_float = c_float()
        self._RPM(address, buf_float)
        return buf_float.value
        
    def render(self):
        
        # read map_name
        maps_temp_array = STR64()
        self._RPM(ADDR_MAPS, maps_temp_array) # Gives us map name in mp_mapname format, and also tells us if we are new to a round or ending a round.
        maps_temp_array_str = cast(pointer(maps_temp_array), c_char_p)
        self.maps_temp = maps_temp_array_str.value
        #Check status of maps, intro, outro
        self.get_map_text()
        
        self.game_time = self._RPM_int(ISINGAME)
        self.is_in_game = (self.game_time != 0 )

        if self.is_in_game:
            if not MOCK:
                self.kills = self._RPM_int(ADDR_KILLS)
                self.deaths = self._RPM_int(ADDR_DEATHS)
                self.local_client_num = self._RPM_int(CG_T)
            
                self._RPM(REFDEF, self.mw2_refdef)
                self._RPM(REFDEF + 0x9904, self.mw2_mypos)
                self._RPM(VIEWANGLEY-0x40, self.mw2_viewy)
                self._RPM(ENTITY, self.mw2_entity)
                self._RPM(CLIENTINFO, self.mw2_clientinfo)
                self.calc_killstreak()
                # sensitivity
                sensitivity_ptr = self._RPM_int(ADDR_SENSITIVITY_PTR_16) + 16
                self.sensitivity = self._RPM_float(sensitivity_ptr)
                print self.sensitivity
                # map name location currently in use, needs formating with regexp to be proper match for our needs.
                map_name_temp = STR64()
                self._RPM(CGS_T + 0x14C, map_name_temp)
                #self._RPM(ADDR_MAP, map_name_temp) removed to keep maintainability
                map_name_temp_str = cast(pointer(map_name_temp), c_char_p)
                self.map_name = map_name_temp_str.value
                match = self.map_name_re.search(self.map_name)
                if match:
                    self.map_name = match.group(1)
                # read game_mode
                game_mode_temp = STR4()
                self._RPM(CGS_T + 0x20, game_mode_temp)
                game_mode_temp_str = cast(pointer(game_mode_temp), c_char_p)
                self.game_mode = game_mode_temp_str.value
            
            self.fov_x = self.mw2_refdef.fov_x
            self.fov_y = self.mw2_refdef.fov_y
            self.local_client_num = self.local_client_num
            self.my_pos = self.mw2_mypos
            self.view_angles = self.mw2_viewy.viewAngles
            self.view_axis = self.mw2_refdef.viewAxis
            
            # views
            self.fov_x = self.mw2_refdef.fov_x
            self.fov_y = self.mw2_refdef.fov_y
            self.view_axis = self.mw2_refdef.viewAxis
            self.view_angles = self.mw2_viewy.viewAngles
            
            # copy entities and cient_info
            for i in range(PLAYERMAX):
                self.player[i].set_values(self.mw2_entity.arr[i], self.mw2_clientinfo.arr[i])
            
            # calculate my team number
            self.local_client_num = self.local_client_num
            for i in range(PLAYERMAX):
                if self.mw2_entity.arr[i].clientNum == self.local_client_num:
                    self.my_team = self.mw2_clientinfo.arr[i].team
                    self.my_player = self.player[i]
                    break
            
            # calculate colors
            for p in self.player:
                if (p.type == ET_PLAYER) and p.valid and p.alive:
                    if (p.team == 1 or p.team == 2) and (p.team == self.my_team):
                        self.enemy = False
                        if p.alive & 0x0001:
                            p.color_esp = COLOR_FRIEND
                            p.color_map = MAP_COLOR_FRIEND
                        else:
                            p.color_esp = COLOR_DEAD
                    else:
                        p.enemy = True
                        if p.alive & 0x0001:
                            if p.perk & 0x8000000:
                                p.color_esp = COLOR_ENEMY_COLDBLOODED
                                p.color_map = MAP_COLOR_ENEMY_COLDBLOODED
                            else:
                                p.color_esp = COLOR_ENEMY
                                p.color_map = MAP_COLOR_ENEMY
                        else:
                            p.color_esp = COLOR_DEAD
                else:
                    #self.enemy = False        # do not change status and keep old one
                    p.color_esp = COLOR_DEAD
                    
            self.my_player.color_esp = 0
            self.my_player.color_map = MAP_COLOR_ME
            # calculate motion vector
            if self.game_time > self._last_game_time:
                k = 1000.0 / (self.game_time - self._last_game_time)
                for idx in range(PLAYERMAX):
                    pos3 = self.player[idx].pos3
                    last_pos3 = self._last_pos3[idx]
                    if self._last_game_time > 0:
                        self.player[idx].motion = VECTOR((pos3.x - last_pos3.x) * k,
                                                         (pos3.y - last_pos3.y) * k,
                                                         (pos3.z - last_pos3.z) * k)
                    last_pos3.x = pos3.x
                    last_pos3.y = pos3.y
                    last_pos3.z = pos3.z
            self._last_game_time = self.game_time
        else:           # not is_in_game
            self.tracked_ent.clear()            # clear all tracked entities
            self._last_game_time = 0
            for p in self._last_pos3:
                p.x = p.y = p.z = 0.0
            
    def get_map_text(self):
        if self.maps_temp == "mpIntro": # triggers on 5 seconds to game match start. also after new host is merged in, countdown from 5
            self.round_start = True
            #print "mpIntro : True"
        else:
            self.round_start = False
            
        if self.maps_temp == "mpOutro": # triggers every round end.
            self.round_end = True   
            #print "mpOutro : True"   
        else:
            self.round_end = False
            
        #if self.maps_temp != "mp_Into" or "mp_Outro":
        #    print self.maps_temp
    def is_host_check(self):
        host_text_temp = STR16()
        self._RPM(GET_HOST_ADDR, host_text_temp)
        host_text = cast(pointer(host_text_temp), c_char_p)
        self.is_host_text = host_text.value
        return self.is_host_text == "localhost"

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
        
    def get_owner_team(self, clientnum):
        owner = self.mw2_entity.arr[clientnum].owner
        if owner >= 0 and owner < PLAYERMAX:
            #print "clientnum=%i, owner=%i, team=%i" % (clientnum, owner, self.mw2_clientinfo.arr[owner].team)
            #print dump_obj(self.mw2_entity.arr[clientnum])
            return self.mw2_clientinfo.arr[owner].team
        
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
