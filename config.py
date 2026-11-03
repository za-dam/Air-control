import ctypes
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

import pyautogui


SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

CAM_WIDTH, CAM_HEIGHT, CAM_FPS = 640, 480, 60

ACTIVE_MARGIN = 0.10

ONE_EURO_MIN_CUTOFF = 0.6
ONE_EURO_BETA = 0.02  

MOUSE_HZ = 120
FOLLOW_TAU = 0.016

PINCH_ON = 0.20
PINCH_OFF = 0.35

JOIN_ON = 1.4   
JOIN_OFF = 1.9

GESTURE_CONFIRM_FRAMES = 2
CLICK_LOOKBACK = 0.15

SHOW_DEBUG = True    