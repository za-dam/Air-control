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

    def get_pointer(self, lm):
        H = self.mp_hands.HandLandmark
        ix, iy = self._px(lm, H.INDEX_FINGER_TIP)
        mx, my = self._px(lm, H.MIDDLE_FINGER_TIP)
        return ((ix + mx) / 2 / self._w, (iy + my) / 2 / self._h)

    def get_points(self, lm):
        return [(p.x * self._w, p.y * self._h) for p in lm.landmark]