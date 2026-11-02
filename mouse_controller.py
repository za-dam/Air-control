import pyautogui
import config


pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

class MouseController() :
    def __init__(self):
        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT

        self.prev_x, self.prev_y = 0, 0
        self.is_pressing = False

    def move_and_click(self, finger_coords, is_drawing):
        if not finger_coords:
            return

        target_x = int(finger_coords["x"] * self.screen_width)
        target_y = int(finger_coords["y"] * self.screen_height)

        smooth_x = self.prev_x + (target_x - self.prev_x) * config.SMOOTHING
        smooth_y = self.prev_y + (target_y - self.prev_y) * config.SMOOTHING
        current_x, current_y = int(smooth_x), int(smooth_y)

        pyautogui.moveTo(current_x, current_y, _pause=False)

        self.prev_x, self.prev_y = current_x, current_y

        if is_drawing:
            if not self.is_pressing:
                pyautogui.mouseDown(_pause=False)
                self.is_pressing = True
        else:
            if self.is_pressing:
                pyautogui.mouseUp(_pause=False)
                self.is_pressing = False
