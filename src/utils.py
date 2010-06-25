from Config import MOUSE_INVERSION
from ctypes import *
import win32con, win32api
from ctypes.wintypes import DWORD, LONG, ULONG, WORD
from directx.types import D3DXVECTOR2
from directx.d3dx import RECT
from math import radians, cos, sin

#
# D3D draw functions
#


#/*
# * DrawText() Format Flags
# */
DT_TOP                      = 0x00000000
DT_LEFT                     = 0x00000000
DT_CENTER                   = 0x00000001
DT_RIGHT                    = 0x00000002
DT_VCENTER                  = 0x00000004
DT_BOTTOM                   = 0x00000008
DT_WORDBREAK                = 0x00000010
DT_SINGLELINE               = 0x00000020
DT_EXPANDTABS               = 0x00000040
DT_TABSTOP                  = 0x00000080
DT_NOCLIP                   = 0x00000100
DT_EXTERNALLEADING          = 0x00000200
DT_CALCRECT                 = 0x00000400
DT_NOPREFIX                 = 0x00000800
DT_INTERNAL                 = 0x00001000


def draw_spot(line, x, y, color):
    draw4(line, x, y - 2, x + 2, y, x, y + 2, x - 2, y, 2, color)

def draw4(line, x1, y1, x2, y2, x3, y3, x4, y4, width, color):
    line.SetWidth(width)
    points = (D3DXVECTOR2 * 5) ((x1,y1), (x2,y2), (x3,y3), (x4,y4), (x1,y1))
    line.Draw(points, len(points), color)
    
def draw_arrow(line, x, y, yaw, color):
    points = (D3DXVECTOR2 * 3) ((-3,5), (0,0), (3.5,5.5))
    points2 = (D3DXVECTOR2 * 3) ((0,0), (0,0), (0,0))
    rad_dir = radians(yaw)
    for i in range(len(points)):
        c = cos(rad_dir)
        s = sin(rad_dir)
        points2[i].x = ((points[i].x * c) - (points[i].y * s)) + x
        points2[i].y = ((points[i].y * c) + (points[i].x * s)) + y
    line.SetWidth(2)
    line.Draw(points2, len(points2), color)

def draw_box(line, x, y, w, h, width, color):
    points = (D3DXVECTOR2 * 5) ((x,y), (x+w,y), (x+w,y+h), (x,y+h), (x,y))
    line.SetWidth(width)
    line.Draw(points, len(points), color)

def draw_line(line, x, y, w, h, width, color):
    points = (D3DXVECTOR2 * 2) ((x,y), (x+w,y+h))
    line.SetWidth(width)
    line.Draw(points, len(points), color)

def draw_line_abs(line, x, y, x2, y2, width, color):
    points = (D3DXVECTOR2 * 2) ((x,y), (x2,y2))
    line.SetWidth(width)
    line.Draw(points, len(points), color)

def draw_string_center(font, x, y, color, text):
    r = RECT(int(x-150), int(y-10), int(x+150), int(y+18))
    font.DrawTextA(None, text, -1, byref(r), DT_CENTER | DT_NOCLIP | DT_SINGLELINE, color)
    
def draw_string_left(font, x, y, w, h, color, text):
    r = RECT(int(x), int(y), int(x+w), int(y-h))
    font.DrawTextA(None, text, -1, byref(r), DT_LEFT | DT_NOCLIP | DT_SINGLELINE, color)



#
# Mouse Input
#

INPUT_MOUSE     = 0
INPUT_KEYBOARD  = 1
INPUT_HARDWARE  = 2

MOUSEEVENTF_MOVE        = 0x0001 #/* mouse move */
MOUSEEVENTF_ABSOLUTE    = 0x8000 #/* absolute move */

class MOUSEINPUT(Structure):
    _fields_ = [ ("dx", LONG),
                 ("dy", LONG),
                 ("mouseData", DWORD),
                 ("dwFlags", DWORD),
                 ("time", DWORD),
                 ("dwExtraInfo", POINTER(ULONG))
                ]

class KEYBDINPUT(Structure):
    _fields_ = [ ("wVk", WORD),
                 ("wScan", WORD),
                 ("dwFlags", DWORD),
                 ("time", DWORD),
                 ("dwExtraInfo", POINTER(ULONG))
                ]
    
class HARDWAREINPUT(Structure):
    _fields_ = [ ("uMsg", DWORD),
                 ("wParamL", WORD),
                 ("wParamH", WORD),
                ]

class _INPUT_UNION(Union):
    _fields_ = [("mi", MOUSEINPUT),
                ("ki", KEYBDINPUT),
                ("hi", HARDWAREINPUT),
                ]

class INPUT(Structure):
    _anonymous_ = ("iu",)
    _fields_ = [ ("type", DWORD),
                 ("iu", _INPUT_UNION)]

def mouse_move(delta_x, delta_y, center_x, center_y):
    mouse_move_x = int(delta_x)
    mouve_move_y = int(delta_y)
    if mouse_move_x == 0 and mouve_move_y == 0:
        return
    fScreenWidth = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) - 1.0
    fScreenHeight = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) - 1.0
    dx = 65535.0 / fScreenWidth
    dy = 65535.0 / fScreenHeight
    fx = (center_x + delta_x) * dx
    if not MOUSE_INVERSION:
        fy = (center_y + delta_y) * dy
    else:
        fy = (center_y - delta_y) * dy
    input = INPUT()
    input.type = INPUT_MOUSE
    input.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
    input.mi.dx = int(fx)
    input.mi.dy = int(fy)
    windll.User32.SendInput(1, byref(input), sizeof(input))
