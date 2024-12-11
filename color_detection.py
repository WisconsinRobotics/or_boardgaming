import numpy as np
import cv2

webcam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
game_board = {"a1": [[0, 0], [100, 100], "empty"], "a2": [[100, 0], [200, 100], "empty"],
              "a3": [[200, 0], [300, 100], "empty"],
              "b1": [[0, 100], [100, 200], "empty"], "b2": [[266, 255], [336, 315], "empty"],
              "b3": [[200, 100], [300, 200], "empty"],
              "c1": [[0, 200], [100, 300], "empty"], "c2": [[100, 200], [200, 300], "empty"],
              "c3": [[200, 200], [300, 300], "empty"]}

while 1:

    _, imageFrame = webcam.read()
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    orange_lower = np.array([10, 140, 140], np.uint8)
    orange_upper = np.array([25, 255, 255], np.uint8)
    orange_mask = cv2.inRange(hsvFrame, orange_lower, orange_upper)

    kernel = np.ones((5, 5), "uint8")

    orange_mask = cv2.dilate(orange_mask, kernel)
    res_orange = cv2.bitwise_and(imageFrame, imageFrame, mask=orange_mask)

    contours, hierarchy = cv2.findContours(orange_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            #print(x, y)
            imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # if game_board["b2"][1][0] > (x + 35) > game_board["b2"][0][0]:
            #     print("O PLACED HERE")


    #cv2.rectangle(imageFrame, (266, 255), (336, 315), (0, 255, 0), 1)

    cv2.imshow("Tic-Tac-Toe", imageFrame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        webcam.release()
        cv2.destroyAllWindows()
        break