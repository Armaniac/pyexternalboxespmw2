import win32api, win32con, win32gui
#from ctypes import *
from Config import *
from directx.d3d import IDirect3D9, IDirect3DDevice9
from directx.types import *
from directx.d3dx import d3dxdll, TestHR, ID3DXFont, ID3DXLine

D3DRS_ZENABLE                      = 7
D3DRS_LIGHTING                     = 137
D3DRS_CULLMODE                     = 22

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
        self._hdc = None            # saving the hdc from BeginPaint
        self._paint_struct = None    # saving the paintstruct from BeginPaint
        # off-screen
        self.hdcMem = None          # dc of off screen bitmap
        self.hbmMem = None          # off-screen bitmap
        self.hbmOld = None          # saving old hmb object
        self.hdc = None             # dc of the window
        self.screen_dc = None       # dc of screen
    
    def init(self):
        """main function"""
        read_game = self.env.read_game
        
        hInstance = win32api.GetModuleHandle()
        wndClass                = win32gui.WNDCLASS()
        wndClass.style          = 0
        wndClass.lpfnWndProc    = lambda hwnd, message, wParam, lParam: self.wndProc(hwnd, message, wParam, lParam)
        wndClass.hInstance      = hInstance
        wndClass.hIcon          = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        wndClass.hCursor        = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wndClass.hbrBackground  = 0
        wndClass.lpszClassName  = str(APP_NAME)                 # not Unicode
        
        win32gui.RegisterClass(wndClass)
    
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST | win32con.WS_EX_COMPOSITED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED,
            APP_NAME,
            APP_NAME,
            win32con.WS_POPUP,
            read_game.wnd_bounding_x,
            read_game.wnd_bounding_y,
            read_game.resolution_x,
            read_game.resolution_y,
            None,
            None,
            hInstance,
            None)
        
        # make a transparent window
        if not MOCK:
            oledll.Dwmapi.DwmExtendFrameIntoClientArea(self.hwnd, byref(MARGINS(-1, -1, -1, -1)))
            compo = c_int()
            oledll.Dwmapi.DwmIsCompositionEnabled(byref(compo))
            if not compo:
                raise Exception("Composition is not activated")
        else:
            pass
        
        
        
        self.init_d3d()
        
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.UpdateWindow(self.hwnd)    


    def init_d3d(self):
        address = windll.d3d9.Direct3DCreate9(UINT(D3D_SDK_VERSION))
        
        params = D3DPRESENT_PARAMETERS()
        params.Windowed            = True
        params.SwapEffect          = D3DSWAPEFFECT.DISCARD  # Required for multi sampling
        params.BackBufferFormat    = D3DFORMAT.A8R8G8B8     # Back buffer format with alpha channel
        params.MultiSampleType     = 0                      # D3DMULTISAMPLE_NONE
        
        self.d3d = POINTER(IDirect3D9)(address)
        self.device = POINTER(IDirect3DDevice9)()
        if not MOCK:
            self.d3d.CreateDevice(0, D3DDEVTYPE.HAL, self.hwnd, D3DCREATE.HARDWARE_VERTEXPROCESSING, byref(params), byref(self.device))
        else:
            self.d3d.CreateDevice(0, D3DDEVTYPE.HAL, self.hwnd, D3DCREATE.SOFTWARE_VERTEXPROCESSING, byref(params), byref(self.device))
        
        self.device.SetRenderState(D3DRS_ZENABLE, False)
        self.device.SetRenderState(D3DRS_LIGHTING, False)
        self.device.SetRenderState(D3DRS_CULLMODE, D3DCULL.NONE)
        
        # common objects        
        d3dxdll.D3DXCreateFontW.restype = TestHR
        self.font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, PLAYER_NAME_SIZE, 0, PLAYER_NAME_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(PLAYER_NAME_FONT)), byref(self.font))
        self.status_font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, 14, 0, 400, 1, 0, 0, 0, 0, 0, LPCWSTR(u"Arial"), byref(self.status_font))
        self.killstreak_font = POINTER(ID3DXFont)()
        d3dxdll.D3DXCreateFontW(self.device, KILLSTREAK_FONT_SIZE, 0, KILLSTREAK_FONT_WEIGHT, 1, 0, 0, 0, 0, 0, LPCWSTR(unicode(KILLSTREAK_FONT_NAME)), byref(self.killstreak_font))
        
        
        self.line = POINTER(ID3DXLine)()
        d3dxdll.D3DXCreateLine.restype = TestHR
        d3dxdll.D3DXCreateLine(self.device, byref(self.line))
        
        self.line.SetWidth(5)
        self.line.SetPattern(0xFFFFFFFF)
        self.line.SetAntialias(True)
        
    def release_d3d(self):
        print "Cleaning D3D"
        if not self.line is None:           self.line.Release()
        if not self.status_font is None:    self.status_font.Release()
        if not self.killstreak_font is None:    self.killstreak_font.Release()
        if not self.font is None:           self.font.Release()
        if not self.device is None:         self.device.Release()
        if not self.d3d is None:            self.d3d.Release()
        
    def BeginPaint(self):
        read_game = self.env.read_game
        if self.env.ticks % 10 == 0:            # check not too often
            if read_game.check_window_moved():
                win32gui.MoveWindow(self.hwnd, read_game.wnd_bounding_x, read_game.wnd_bounding_y,
                                    read_game.resolution_x, read_game.resolution_y, False)
        
        self.device.Clear(0, None, D3DCLEAR.TARGET, 0x00000000, 1, 0)
        self.device.BeginScene()        
    
    def EndPaint(self):
        self.device.EndScene()
        if not PROFILING:
            self.device.Present(None, None, self.hwnd, None)    
    
    def wndProc(self, hwnd, message, wParam, lParam):    
        if message == win32con.WM_DESTROY:        
            win32gui.PostQuitMessage(0)
            return 0                 
        else:
            return win32gui.DefWindowProc(hwnd, message, wParam, lParam)
