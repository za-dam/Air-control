import ctypes
from ctypes import wintypes

_user32 = ctypes.windll.user32

MOVE, LEFTDOWN, LEFTUP, ABSOLUTE = 0x0001, 0x0002, 0x0004, 0x8000
INPUT_MOUSE = 0

ULONG_PTR = ctypes.c_size_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]

    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]


def _send(flags, dx=0, dy=0):
    inp = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dx, dy, 0, flags, 0, 0))
    _user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def move_abs(x, y, screen_w, screen_h):
    nx = int(x * 65535 / max(screen_w - 1, 1))
    ny = int(y * 65535 / max(screen_h - 1, 1))
    _send(MOVE | ABSOLUTE, nx, ny)


def left_down():
    _send(LEFTDOWN)


def left_up():
    _send(LEFTUP)