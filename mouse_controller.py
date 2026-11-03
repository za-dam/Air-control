import math
import threading
import time
from collections import deque

import config
import win_mouse
from one_euro import OneEuroFilter


class MouseController:
    def __init__(self):
        self.w, self.h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.fx = OneEuroFilter(config.ONE_EURO_MIN_CUTOFF, config.ONE_EURO_BETA)
        self.fy = OneEuroFilter(config.ONE_EURO_MIN_CUTOFF, config.ONE_EURO_BETA)

        self._lock = threading.Lock()
        self._target = None
        self._want_press = False
        self._pos = None
        self._pressed = False
        self._running = True
        self._history = deque(maxlen=90)
        self._clicks = deque()

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    @staticmethod
    def _to_active_zone(v):
        m = config.ACTIVE_MARGIN
        return min(max((v - m) / (1 - 2 * m), 0.0), 1.0)

    def update(self, point, is_drawing, t, follow=True):
        with self._lock:
            if point is None:
                self._target = None
                self._want_press = False
                self._history.clear()
                self.fx.reset()
                self.fy.reset()
                return

            self._want_press = is_drawing
            if not follow:
                return

            x = self._to_active_zone(point[0]) * (self.w - 1)
            y = self._to_active_zone(point[1]) * (self.h - 1)
            target = (self.fx(x, t), self.fy(y, t))
            self._target = target
            self._history.append((t, target))

    def freeze(self):
        with self._lock:
            pos = self._position_before(time.perf_counter() - config.CLICK_LOOKBACK)
            if pos is not None:
                self._target = pos
            return pos

    def click(self, button="left"):
        pos = self.freeze()
        if pos is None:
            return
        with self._lock:
            self._clicks.append((button, pos))

    def _position_before(self, t_cut):
        for t, pos in reversed(self._history):
            if t <= t_cut:
                return pos
        return self._history[0][1] if self._history else self._target

    def _loop(self):
        interval = 1.0 / config.MOUSE_HZ
        last = time.perf_counter()

        while self._running:
            now = time.perf_counter()
            dt = now - last
            last = now

            with self._lock:
                target, want = self._target, self._want_press
                clicks = list(self._clicks)
                self._clicks.clear()

            for button, pos in clicks:
                self._pos = pos
                win_mouse.move_abs(round(pos[0]), round(pos[1]), self.w, self.h)
                win_mouse.click(button)

            if target is not None:
                if self._pos is None:
                    self._pos = target
                else:
                    a = 1 - math.exp(-dt / config.FOLLOW_TAU)
                    self._pos = (
                        self._pos[0] + (target[0] - self._pos[0]) * a,
                        self._pos[1] + (target[1] - self._pos[1]) * a,
                    )
                win_mouse.move_abs(round(self._pos[0]), round(self._pos[1]), self.w, self.h)

            if want and not self._pressed:
                win_mouse.left_down()
                self._pressed = True
            elif not want and self._pressed:
                win_mouse.left_up()
                self._pressed = False

            time.sleep(max(0.0, interval - (time.perf_counter() - now)))

    def close(self):
        self._running = False
        self._thread.join(timeout=1)
        if self._pressed:
            win_mouse.left_up()