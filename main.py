import time
import cv2

import config
from camera import Camera
from hand_tracker import HandTracker
from mouse_controller import MouseController
from gestures import GestureRecognizer, Gesture

FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_status(frame, gesture, debug):
    cv2.putText(frame, gesture.name, (10, 30), FONT, 1, (0, 255, 0), 2)
    if config.SHOW_DEBUG:
        for i, (key, val) in enumerate(debug.items()):
            text = f"{key}: {val:.2f}" if isinstance(val, float) else f"{key}: {val}"
            cv2.putText(frame, text, (10, 60 + 22 * i), FONT, 0.55, (255, 255, 0), 1)


def main():
    camera = Camera()
    tracker = HandTracker()
    mouse = MouseController()
    recognizer = GestureRecognizer()

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                break

            t = time.perf_counter()
            hand = tracker.find_hand(frame)

            if hand:
                gesture, event = recognizer.update(tracker.get_points(hand))

                if event == Gesture.CLICK:
                    mouse.click("left")
                elif event == Gesture.RIGHT_CLICK:
                    mouse.click("right")
                elif event == Gesture.FIST:
                    mouse.freeze()

                follow = gesture in (Gesture.NONE, Gesture.DRAW)
                mouse.update(tracker.get_pointer(hand),
                             gesture == Gesture.DRAW, t, follow)
            else:
                gesture, _ = recognizer.update(None)
                mouse.update(None, False, t)

            draw_status(frame, gesture, recognizer.debug)
            camera.show(frame)
            if camera.check_exit_signal():
                break
    finally:
        mouse.close()
        camera.release()


if __name__ == "__main__":
    main()