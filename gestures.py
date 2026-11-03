import math
from enum import Enum, auto

import config


class Gesture(Enum):
    NONE = auto()         # курсор просто двигается
    CLICK = auto()        # щипок : большой + указательный
    DRAW = auto()         # указательный и средний вместе
    RIGHT_CLICK = auto()  # щипок : большой + средний
    FIST = auto()         # пауза


WRIST = 0
THUMB_TIP = 4
INDEX_MCP, INDEX_PIP, INDEX_TIP = 5, 6, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP = 9, 10, 12
RING_PIP, RING_TIP = 14, 16
PINKY_PIP, PINKY_TIP = 18, 20


def _curled(pts, tip, pip):
    return math.dist(pts[tip], pts[WRIST]) < math.dist(pts[pip], pts[WRIST])


class GestureRecognizer:
    def __init__(self):
        self.current = Gesture.NONE
        self.debug = {}
        self._candidate = Gesture.NONE
        self._count = 0
        self._raw_prev = Gesture.NONE
        self._joined = False

    def _raw(self, pts):
        hand = math.dist(pts[WRIST], pts[MIDDLE_MCP]) or 1e-6

        curled = {
            "I": _curled(pts, INDEX_TIP, INDEX_PIP),
            "M": _curled(pts, MIDDLE_TIP, MIDDLE_PIP),
            "R": _curled(pts, RING_TIP, RING_PIP),
            "P": _curled(pts, PINKY_TIP, PINKY_PIP),
        }
        thumb_index = math.dist(pts[THUMB_TIP], pts[INDEX_TIP]) / hand
        thumb_middle = math.dist(pts[THUMB_TIP], pts[MIDDLE_TIP]) / hand
        bases = math.dist(pts[INDEX_MCP], pts[MIDDLE_MCP]) or 1e-6
        join = math.dist(pts[INDEX_TIP], pts[MIDDLE_TIP]) / bases

        self.debug = {
            "thumb-index": thumb_index,
            "thumb-middle": thumb_middle,
            "join": join,
            "curled": "".join(k if v else "-" for k, v in curled.items()),
        }

        if all(curled.values()):
            self._joined = False
            return Gesture.FIST

        pinch = {Gesture.CLICK: thumb_index, Gesture.RIGHT_CLICK: thumb_middle}
        prev = self._raw_prev
        if prev in pinch and pinch[prev] < config.PINCH_OFF:
            return prev
        gesture, ratio = min(pinch.items(), key=lambda kv: kv[1])
        if ratio < config.PINCH_ON:
            return gesture

        two_up = (not curled["I"] and not curled["M"]
                  and curled["R"] and curled["P"])
        if two_up:
            limit = config.JOIN_OFF if self._joined else config.JOIN_ON
            self._joined = join < limit
        else:
            self._joined = False
        return Gesture.DRAW if self._joined else Gesture.NONE

    def update(self, pts):
        if pts:
            raw = self._raw(pts)
        else:
            raw = Gesture.NONE
            self._joined = False
            self.debug = {}
        self._raw_prev = raw

        if raw == self._candidate:
            self._count += 1
        else:
            self._candidate, self._count = raw, 1

        event = None
        if (self._candidate != self.current
                and self._count >= config.GESTURE_CONFIRM_FRAMES):
            prev, self.current = self.current, self._candidate
            event = self.current
            if prev == Gesture.FIST and event in (Gesture.CLICK, Gesture.RIGHT_CLICK):
                event = None
        return self.current, event