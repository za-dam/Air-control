import cv2


class Camera() :
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("ERROR : Couldn't access the webcam.")

    def check_exit_signal(self) :
        if cv2.waitKey(10) & 0xFF == ord('q'):
            return True
        return False

    def get_frame(self) :
        success, img = self.cap.read()

        if not success :
            print("Warning : Failed to read frame from the camera.")
            return None
        
        frame = cv2.flip(img, 1)
        cv2.imshow("Air Painter Visual", frame)

        return frame

    def release(self) :
        self.cap.release()
        cv2.destroyAllWindows()