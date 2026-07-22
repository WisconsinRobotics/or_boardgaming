import cv2
import os
import time

class Camera:

    def __init__(self):
        print('Starting Camera')
        self.CAMERA = cv2.VideoCapture(0)
        if not self.CAMERA.isOpened():
            self.CAMERA = None
            raise ValueError("Cannot open camera")

        print('Camera successfully started')

    def __del__(self):
        if not (self.CAMERA is None) and self.CAMERA.isOpened():
            self.CAMERA.release()
        cv2.destroyAllWindows()

    def clickPicture(self, count = 1, saveimg = True):
        res, frame = self.CAMERA.read()
        if res:
            if saveimg:
                os.makedirs('../images/', exist_ok = True)
                cv2.imwrite(f'../images/img_{count}_{int(time.time())}.png', frame)
            return frame
        else:
            print(f'WARNING: Cant receive frame (stream end?). trying again. try {count}')
            if count < 3:
                time.sleep(0.2)
                return self.clickPicture(count + 1, saveimg=saveimg)
            else:
                print('ERROR: camera error. pic not clicked even after 3 attempts. sadge')
                return None

if __name__ == "__main__":
    cam = Camera()
    cam.clickPicture()
    print("clicked pic")
