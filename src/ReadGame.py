import win32api, win32con, win32gui, win32process
from time import sleep
from structs import *
from Config import *

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

        # pre-mashed info
        self.fov_x = 0.0                # field of view
        self.fov_y = 0.0
        self.killstreak = 0             # current killstreak number
        self.local_client_num = 0
        self.my_team = 0                # my team number
        self.my_pos = VECTOR()          # my position vector
        self.view_angles = VECTOR()
        self.view_axis = [ VECTOR(), VECTOR(), VECTOR() ]
        
        self.player = [Player() for i in range(PLAYERMAX)]
        self.my_player = self.player[0]
        
        # internal private
        self._last_deaths = 0 
        self._last_kills = 0
    
    def init(self):
        print "External BoxESP+bot version 5.0 by Sph4ck"
        print "for COD6 MW2 - build 1.1.195"
        print "- works on Vista/Win7 with Aero theme activated"
        print
        print "Waiting for COD6 game..."
        while self.mw2_hwnd == 0:
            self.mw2_hwnd = win32gui.FindWindow(None, COD_WINDOW_NAME)
            sleep(0.050)
        print "COD6 game found."
        while self.mw2_pid == 0:
            tid, self.mw2_pid = win32process.GetWindowThreadProcessId(self.mw2_hwnd)
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
        
    def render(self):
        self.is_in_game = ( self._RPM_int(ISINGAME) != 0 )

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
            
            self.fov_x = self.mw2_refdef.fov_x
            self.fov_y = self.mw2_refdef.fov_y
            self.local_client_num = self.local_client_num
            self.my_pos = self.mw2_mypos
            self.view_angles = self.mw2_viewy.viewAngles
            self.view_axis = self.mw2_refdef.viewAxis
            
            self.calc_killstreak()
            
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
                    self.enemy = False
                    p.color_esp = COLOR_DEAD
                    
            self.my_player.color_esp = 0
            self.my_player.color_map = MAP_COLOR_ME
            
    def start_game(self):
        self._last_deaths = 0
        self._last_kills = 0
        self.killstreak = 0
        
    def calc_killstreak(self):
        if self.deaths != self._last_deaths:
            self._last_deaths = self.deaths
            self._last_kills = self.kills
        if self.kills < self._last_kills:
            self._last_kills = self.kills
        self.killstreak = self.kills - self._last_kills

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
