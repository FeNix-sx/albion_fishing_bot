import numpy as np
from random import uniform, randint
from mss.windows import MSS as mss
from PIL import Image
import time
import pyautogui as pg
import cv2

template = cv2.imread("float_small.jpg", cv2.IMREAD_GRAYSCALE)
w, h = template.shape[::-1]
print(w, h)
left = 2560
height = 1440
monitor = {"top": 700, "left": 1100, "width": 350, "height": 100}


def get_monitor(monitor: dict):
    with mss() as sct:
        img = np.array(sct.grab(monitor))
        return img


def get_time_difference(time_list):
    time_list.append(time.time())
    if len(time_list) > 1:
        time_difference = time_list[-1] - time_list[-2]
        return time_difference
    else:
        return 0


def main():
    time_list = []
    x = 0
    btn_click = False

    while True:
        last_time = time.time()
        img = get_monitor(monitor)
        # cv2.imshow("OpenCV/Numpy normal", img)
        print("\rfps: {}".format(1 / (time.time() - last_time)), x, end="")
        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.7)

        if np.size(loc) == 0 and btn_click == True:
            pg.mouseUp(button='left')
            print("\n Поймал")
            btn_click = False

        for pt in zip(*loc[::-1]):
            cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 3)
            x = pt[0]
            time_list.append(time.time())
            print("\nx = " , x)

            if x < randint(190, 215):
                # print("\rGGGGGGGGGGG!", end="")
                pg.mouseDown(button="left")
            elif x > randint(220, 235):
                # print("\r===========!", end="")
                pg.mouseUp(button='left')

            btn_click = True
            time.sleep(uniform(0.02, 0.05))
            break

        # cv2.imshow("Frame", img)

        key = cv2.waitKey(1)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
