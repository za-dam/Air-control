from camera import Camera
from hand_tracker import HandTracker
from mouse_controller import MouseController


def main() :

    camera = Camera()
    tracker = HandTracker()
    mouse = MouseController()
    ochko_status = False

    while True :

        frame = camera.get_frame()
        if frame is None :
            break

        hand_landmarks = tracker.find_hand(frame)
        if not hand_landmarks:
            continue

        index_finger = tracker.get_finger_tip(hand_landmarks, "INDEX")
        thumb = tracker.get_finger_tip(hand_landmarks, "THUMB")

        if tracker.check_ok_gesture(index_finger, thumb):
            ochko_status = True
        else:
            ochko_status = False

        mouse.move_and_click(index_finger, is_drawing=ochko_status)

        if camera.check_exit_signal():
            break

    camera.release()

if __name__ == "__main__":
    main()