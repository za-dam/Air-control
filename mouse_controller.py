import pyautogui
import config
from one_euro import OneEuroFilter
import math
import threading
import time


pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False


class MouseController() :
    def __init__(self) :
        self.w, self.h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.fx = OneEuroFilter(config.ONE_EURO_MIN_CUTOFF, config.ONE_EURO_BETA)
        self.fy = OneEuroFilter(config.ONE_EURO_MIN_CUTOFF, config.ONE_EURO_BETA)

        self._lock = threading.Lock()
        self._target = None
        self._want_press = False
        self._pos = None
        self._pressed = False
        self._running = True

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    @staticmethod
    def _to_active_zone(v) :
        m = config.ACTIVE_MARGIN
        return min(max((v - m) / (1 - 2 * m), 0.0), 1.0)

    def update(self, point, is_drawing, t) :
        with self._lock:
            if point is None:
                self._target = None
                self._want_press = False
                self.fx.reset()
                self.fy.reset()
                return

            x = self._to_active_zone(point[0]) * (self.w - 1)
            y = self._to_active_zone(point[1]) * (self.h - 1)
            self._target = (self.fx(x, t), self.fy(y, t))
            self._want_press = is_drawing

    def _loop(self) :
        interval = 1.0 / config.MOUSE_HZ
        last = time.perf_counter()

        while self._running:
            now = time.perf_counter()
            dt = now - last
            last = now

            with self._lock:
                target, want = self._target, self._want_press

            if target is not None:
                if self._pos is None:
                    self._pos = target
                else:
                    a = 1 - math.exp(-dt / config.FOLLOW_TAU)
                    self._pos = (
                        self._pos[0] + (target[0] - self._pos[0]) * a,
                        self._pos[1] + (target[1] - self._pos[1]) * a,
                    )
                pyautogui.moveTo(round(self._pos[0]), round(self._pos[1]), _pause=False)

            if want and not self._pressed:
                pyautogui.mouseDown(_pause=False)
                self._pressed = True
            elif not want and self._pressed:
                pyautogui.mouseUp(_pause=False)
                self._pressed = False

            time.sleep(max(0.0, interval - (time.perf_counter() - now)))

    def close(self):
        self._running = False
        self._thread.join(timeout=1)
        if self._pressed:
            pyautogui.mouseUp(_pause=False)