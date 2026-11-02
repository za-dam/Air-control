import cv2
import config


class Camera() :
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAM_FPS)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            print("ERROR : Couldn't access the webcam.")

    def check_exit_signal(self) :
        return cv2.waitKey(1) & 0xFF == ord('q')

    def get_frame(self) :
        success, img = self.cap.read()

        if not success :
            print("Warning : Failed to read frame from the camera.")
            return None
        
        return cv2.flip(img, 1)

    def show(self, frame):
        cv2.imshow("Air Painter Visual", frame)

    def release(self) :
        self.cap.release()
        cv2.destroyAllWindows()