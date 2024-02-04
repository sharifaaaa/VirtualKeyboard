import cv2
from cvzone.HandTrackingModule import HandDetector
import math
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller,Key
import time


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8)

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]"],
        ["A", "S", "D", "F", "G","H", "J", "K", "L", ";", "Del"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "',", "?", "/"]]
finalText = ""
length = float(0)
keyboard = Controller()
class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

#buttonList = [Button([100 * j + 50, 100 * i + 50], key) for i, row in enumerate(keys) for j, key in enumerate(row)]
buttonList = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        if key == "Del":
            # Making the width of the 'Del' button twice larger
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key, size=[85*2, 85]))
        else:
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)

        # Centralizing text for all buttons, especially for the wider 'Del' button
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, 5, 5)[0]
        textX = x + (w - text_size[0]) // 2
        textY = y + (h + text_size[1]) // 2

        cv2.putText(img, button.text, (textX, textY), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)

    return img

# Add a variable to store the time of the last key press
lastKeyPressTime = 0
keyPressDelay = 0.4  # Delay in seconds between key presses

while True:
    success, img = cap.read()
    if success:
        hands, img = detector.findHands(img)
        img = drawAll(img, buttonList)
        if hands:
            for hand in hands:
                lmList = hand["lmList"]
                if len(lmList) > 12:
                    for button in buttonList:
                        x, y = button.pos
                        w, h = button.size
                        cx, cy = lmList[8][0], lmList[8][1]

                        if x < cx < x + w and y < cy < y + h:
                            length, info, img = detector.findDistance(lmList[8][:2], lmList[12][:2], img)
                            color = (0, 255, 0) if 40 < length < 90 else (175, 0, 175)
                            # cv2.rectangle(img, button.pos, (x + w, y + h), color, cv2.FILLED)
                            #Hover keys
                            cv2.rectangle(img, (x - 10, y - 10), (x + w + 10, y + h + 10), color, cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255),4)
                            # Check if in clicking range and if enough time has passed since last key press
                            currentTime = time.time()
                            if 40 < length < 90 and currentTime - lastKeyPressTime > keyPressDelay:
                                if button.text == "Del":
                                    finalText = finalText[:-1]  # Remove last character from finalText
                                    keyboard.press(Key.backspace)  # Simulate backspace keypress
                                    keyboard.release(Key.backspace)
                                    print("Delete Pressed",length)

                                else:
                                    lastKeyPressTime = currentTime
                                    finalText += button.text
                                    keyboard.press(button.text)
                                    keyboard.release(button.text)
                                    print("Key Pressed:", button.text , length)
                                    time.sleep(0.1)  # Additional delay to ensure key press is registered
        #create a place Holder
        cv2.rectangle(img, (50,350),(700,450), (175,0,175), cv2.FILLED)
        cv2.putText(img, finalText, (60, 425), cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255), 6)
        ####
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

