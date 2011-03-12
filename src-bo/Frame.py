from Config import * #@UnusedWildImport
from directx.d3d import IDirect3D9, IDirect3DDevice9
from directx.types import * #@UnusedWildImport
from directx.d3dx import d3dxdll, TestHR, ID3DXFont, ID3DXLine, ID3DXSprite

D3DRS_ZENABLE                      = 7
D3DRS_LIGHTING                     = 137
D3DRS_CULLMODE                     = 22

WS_EX_TOPMOST       = 8
WS_EX_COMPOSITED    = 0x02000000
WS_EX_TRANSPARENT   = 32
WS_EX_LAYERED       = 0x00080000

WS_POPUP            = 0x80000000

WNDPROC = WINFUNCTYPE(c_long, c_int, c_uint, c_int, c_int)

class WNDCLASS(Structure):
    _fields_ = [('style', c_uint),
                ('lpfnWndProc', WNDPROC),
                ('cbClsExtra', c_int),
                ('cbWndExtra', c_int),
                ('hInstance', c_int),
                ('hIcon', c_int),
                ('hCursor', c_int),
                ('hbrBackground', c_int),
                ('lpszMenuName', c_char_p),
                ('lpszClassName', c_char_p)]

class PAINTSTRUCT(Structure):
    _fields_ = [('hdc', c_int),
                ('fErase', c_int),
                ('rcPaint', RECT),
                ('fRestore', c_int),
                ('fIncUpdate', c_int),
                ('rgbReserved', c_char * 32)]

def wndProc(hwnd, message, wParam, lParam):    
    if message == 2:                    #WM_DESTROY        
        windll.user32.PostQuitMessage(0)
        return 0                 
    else:
        return windll.user32.DefWindowProcA(c_int(hwnd), c_int(message), c_int(wParam), c_int(lParam))

class MARGINS(Structure):
    _fields_ = [ ("cxLeftWidth", c_int),
                 ("cxRightWidth", c_int),
                 ("cyTopHeight", c_int),
                 ("cyBottomHeight", c_int),]



class Rect(object):
    def __init__(self, initlist=None):
        self.left = initlist[0]
        self.top = initlist[1]
        self.right = initlist[2]
        self.bottom = initlist[3]

class Frame(object):
    def __init__(self, env):
        self.env = env
        self.hwnd = None
    
    def init_create_window(self):
        # this is to be called by a specific thread that will be the owner
        read_game = self.env.read_game
        
        hInstance = windll.kernel32.GetModuleHandleA(None)
        wndClass                = WNDCLASS()
        wndClass.style          = 0
        wndClass.lpfnWndProc    = WNDPROC(wndProc)
        wndClass.hInstance      = hInstance
        wndClass.hIcon          = windll.user32.LoadIconA(0, 32512)     # 32512 = IDI_APPLICATION
        wndClass.hCursor        = windll.user32.LoadCursorA(0, 32512)   # 32512 = IDC_ARROW
        wndClass.hbrBackground  = 0
        wndClass.lpszClassName  = str(APP_NAME)                 # not Unicode
        wndClass.lpszMenuName   = None
        
        if not windll.user32.RegisterClassA(byref(wndClass)):
            raise WinError()
        
        self.wndClass = wndClass        # make sure it is not garbage-collected

        self.hwnd = windll.user32.CreateWindowExA(
            WS_EX_TOPMOST | WS_EX_COMPOSITED | WS_EX_TRANSPARENT | WS_EX_LAYERED,
            APP_NAME,
            APP_NAME,
            WS_POPUP,
            read_game.wnd_bounding_x,
            read_game.wnd_bounding_y,
            read_game.resolution_x,
            read_game.resolution_y,
            None,
            None,
            hInstance,
            None)
        
        # make a transparent window
        if not FAKE:
            oledll.Dwmapi.DwmExtendFrameIntoClientArea(self.hwnd, byref(MARGINS(-1, -1, -1, -1)))
            compo = c_int()
            oledll.Dwmapi.DwmIsCompositionEnabled(byref(compo))
            if not compo:
                raise Exception("Composition is not activated")
            
        windll.user32.ShowWindow(self.hwnd, 1)      # SW_SHOWNORMAL = 1
        windll.user32.UpdateWindow(self.hwnd)
        
    def pump_messages(self):
        quit = False
        while not quit:
            msg = MSG()
            pending = windll.user32.GetMessageA(pointer(msg), self.hwnd, 0, 0)      # PM_REMOVE = 1
            if (msg.message & 0xFFFF == 18):         # WM_QUIT = 18
                break
            windll.user32.TranslateMessage(byref(msg))
            windll.user32.DispatchMessageA(byref(msg))

    def init_d3d(self):
        address = windll.d3d9.Direct3DCreate9(UINT(D3D_SDK_VERSION))
        
        params = D3DPRESENT_PARAMETERS()
        params.Windowed            = True
        params.SwapEffect          = D3DSWAPEFFECT.DISCARD  # Required for multi sampling
        params.BackBufferFormat    = D3DFORMAT.A8R8G8B8     # Back buffer format with alpha channel
        params.MultiSampleType     = 0                      # D3DMULTISAMPLE_NONE
        
        self.d3d = POINTER(IDirect3D9)(address)
        self.device = POINTER(IDirect3DDevice9)()
        if not FAKE:
            self.d3d.CreateDevice(0, D3DDEVTYPE.HAL, self.hwnd, D3DCREATE.HARDWARE_VERTEXPROCESSING, byref(params), byref(self.device))
        else:
            self.d3d.CreateDevice(0, D3DDEVTYPE.HAL, self.hwnd, D3DCREATE.SOFTWARE_VERTEXPROCESSING, byref(params), byref(self.device))
        
        self.device.SetRenderState(D3DRS_ZENABLE, False)
        self.device.SetRenderState(D3DRS_LIGHTING, False)
        self.device.SetRenderState(D3DRS_CULLMODE, D3DCULL.NONE)
        
        # common objects        
        d3dxdll.D3DXCreateFontW.restype = TestHR
        self.font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, PLAYER_NAME_SIZE, 0, PLAYER_NAME_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(PLAYER_NAME_FONT)), byref(self.font)) #@UndefinedVariable
        self.status_font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, 14, 0, 400, 1, 0, 0, 0, 0, 0, LPCWSTR(u"Arial"), byref(self.status_font)) #@UndefinedVariable
        self.killstreak_font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, KILLSTREAK_FONT_SIZE, 0, KILLSTREAK_FONT_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(KILLSTREAK_FONT_NAME)), byref(self.killstreak_font)) #@UndefinedVariable
        self.rage_font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, RAGE_FONT_SIZE, 0, RAGE_FONT_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(RAGE_FONT_NAME)), byref(self.rage_font)) #@UndefinedVariable
        self.ammo_font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, AMMO_COUNTER_FONT_SIZE, 0, AMMO_COUNTER_FONT_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(AMMO_COUNTER_FONT_NAME)), byref(self.ammo_font)) #@UndefinedVariable
        self.c4_font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, C4AUTOFIRE_FONT_SIZE, 0, C4AUTOFIRE_FONT_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(C4AUTOFIRE_FONT_NAME)), byref(self.c4_font)) #@UndefinedVariable
        self.cooking = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, GRENADECOOKING_FONT_SIZE, 0, GRENADECOOKING_FONT_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(GRENADECOOKING_FONT_NAME)), byref(self.cooking)) #@UndefinedVariable
        
        
        self.line = POINTER(ID3DXLine)()
        d3dxdll.D3DXCreateLine.restype = TestHR
        d3dxdll.D3DXCreateLine(self.device, byref(self.line)) #@UndefinedVariable
        
        self.line.SetWidth(5)
        self.line.SetPattern(0xFFFFFFFF)
        self.line.SetAntialias(True)
        
        self.sprite = POINTER(ID3DXSprite)()
        d3dxdll.D3DXCreateSprite(self.device, byref(self.sprite)) #@UndefinedVariable
        
    def release_d3d(self):
        if not self.line is None:               self.line.Release()
        if not self.status_font is None:        self.status_font.Release()
        if not self.killstreak_font is None:    self.killstreak_font.Release()
        if not self.rage_font is None:          self.rage_font.Release()
        if not self.ammo_font is None:          self.ammo_font.Release()
        if not self.font is None:               self.font.Release()
        if not self.device is None:             self.device.Release()
        if not self.d3d is None:                self.d3d.Release()
        if not self.sprite is None:             self.sprite.Release()
        
    def BeginPaint(self):
        read_game = self.env.read_game
        if self.env.ticks % 10 == 0:            # check not too often
            if read_game.check_window_moved():
                windll.user32.MoveWindow(self.hwnd, read_game.wnd_bounding_x, read_game.wnd_bounding_y,
                                    read_game.resolution_x, read_game.resolution_y, False)
        
        self.device.Clear(0, None, D3DCLEAR.TARGET, 0x00000000, 1, 0)
        self.device.BeginScene()        
    
    def EndPaint(self):
        self.device.EndScene()
        if not PROFILING:
            self.device.Present(None, None, self.hwnd, None)    
    
    def wndProc(self, hwnd, message, wParam, lParam):    
        if message == 2:                    #WM_DESTROY        
            windll.user32.PostQuitMessage(0)
            return 0                 
        else:
            return windll.user32.DefWindowProcA(hwnd, message, wParam, lParam)
