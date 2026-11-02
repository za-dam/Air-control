import cv2
import math
import mediapipe as mp
import config

class HandTracker:
    def __init__(self) :
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.is_pinching = False
        self._w = self._h = 1

    def find_hand(self, frame) :
        self._h, self._w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        
        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, lm, self.mp_hands.HAND_CONNECTIONS)
            return lm
        
        self.is_pinching = False
        return None

    def _px(self, lm, idx) :
        p = lm.landmark[idx]
        return p.x * self._w, p.y * self._h

    def get_pinch_point(self, lm) :
        H = self.mp_hands.HandLandmark
        tx, ty = self._px(lm, H.THUMB_TIP)
        ix, iy = self._px(lm, H.INDEX_FINGER_TIP)
        return ((tx + ix) / 2 / self._w, (ty + iy) / 2 / self._h)

    def check_pinch(self, lm):
        H = self.mp_hands.HandLandmark
        tx, ty = self._px(lm, H.THUMB_TIP)
        ix, iy = self._px(lm, H.INDEX_FINGER_TIP)
        wx, wy = self._px(lm, H.WRIST)
        mx, my = self._px(lm, H.MIDDLE_FINGER_MCP)

        hand_size = math.hypot(wx - mx, wy - my) or 1e-6
        ratio = math.hypot(tx - ix, ty - iy) / hand_size

        if self.is_pinching:
            if ratio > config.PINCH_OFF:
                self.is_pinching = False
        elif ratio < config.PINCH_ON:
            self.is_pinching = True
            
        return self.is_pinching