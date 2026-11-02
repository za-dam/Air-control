import cv2
import math
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.is_ok_active = False

    def find_hand(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            return hand_landmarks
        return None

    def get_finger_tip(self, hand_landmarks, finger_name):
        if finger_name == "INDEX":
            landmark_id = self.mp_hands.HandLandmark.INDEX_FINGER_TIP
        elif finger_name == "THUMB":
            landmark_id = getattr(self.mp_hands.HandLandmark, 'THUMB_TIP', 4)
        else:
            return None

        pt = hand_landmarks.landmark[landmark_id]
        return {"x": pt.x, "y": pt.y}

    def check_ok_gesture(self, index_finger, thumb):
        if not index_finger or not thumb:
            return False
            
        distance = math.sqrt((index_finger["x"] - thumb["x"])**2 + (index_finger["y"] - thumb["y"])**2)

        if self.is_ok_active :
            if distance > 0.055 :
                self.is_ok_active = False
        else :
            if distance < 0.035:
                self.is_ok_active = True

        return self.is_ok_active
