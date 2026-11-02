from camera import Camera
from hand_tracker import HandTracker
from mouse_controller import MouseController
import time



def main() :

    camera = Camera()
    tracker = HandTracker()
    mouse = MouseController()
    ochko_status = False

    try :
        while True :
            frame = camera.get_frame()
            if frame is None :
                break

            t = time.perf_counter()
            hand = tracker.find_hand(frame)

            if hand :
                mouse.update(tracker.get_pinch_point(hand), tracker.check_pinch(hand), t)
            else :
                mouse.update(None, False, t)

            camera.show(frame)
            if camera.check_exit_signal() :
                break
    finally :
        mouse.close()
        camera.release()

if __name__ == "__main__":
    main()