import cv2
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller, Key
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8)

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "Del"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "'", "?", "/"],
        ["Notepad"]]  # Notepad button on its own row

finalText = ""
keyboard = Controller()
typingInNotepad = False  # Variable to toggle between Notepad and placeholder

class Button:
    def __init__(self, pos, text, size=[85, 85], color=(255, 0, 255)):
        self.pos = pos
        self.size = size
        self.text = text
        self.color = color

buttonList = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        if key == "Del":
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key, size=[85 * 2, 85]))
        elif key == "Notepad":
            buttonList.append(Button([50, 100 * i + 50], key, size=[700, 85], color=(255, 0, 255)))  # Default purple color
        else:
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

# Hysteresis and Smoothing
upper_threshold = 90
lower_threshold = 40
threshold_buffer = 10
distance_history = []
smoothing_frames = 5
within_press_range = False

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), button.color, cv2.FILLED)
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, 5, 5)[0]
        textX = x + (w - text_size[0]) // 2
        textY = y + (h + text_size[1]) // 2
        cv2.putText(img, button.text, (textX, textY), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
    return img

lastKeyPressTime = 0
keyPressDelay = 0.4

while True:
    success, img = cap.read()
    if success:
        hands, img = detector.findHands(img)
        img = drawAll(img, buttonList)
        if hands:
            for hand in hands:
                lmList = hand["lmList"]
                if len(lmList) > 12:
                    length, info, img = detector.findDistance(lmList[8][:2], lmList[12][:2], img)
                    distance_history.append(length)
                    if len(distance_history) > smoothing_frames:
                        distance_history.pop(0)
                    avg_distance = sum(distance_history) / len(distance_history)

                    # Hysteresis
                    if avg_distance < lower_threshold + threshold_buffer:
                        within_press_range = True
                    elif avg_distance > upper_threshold - threshold_buffer:
                        within_press_range = False

                    for button in buttonList:
                        x, y = button.pos
                        w, h = button.size
                        cx, cy = lmList[8][0], lmList[8][1]

                        if x < cx < x + w and y < cy < y + h:
                            color = (0, 255, 0) if within_press_range else button.color
                            cv2.rectangle(img, (x - 10, y - 10), (x + w + 10, y + h + 10), color, cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            currentTime = time.time()
                            if within_press_range and currentTime - lastKeyPressTime > keyPressDelay:
                                if button.text == "Del":
                                    finalText = finalText[:-1]
                                    if typingInNotepad:
                                        keyboard.press(Key.backspace)
                                        keyboard.release(Key.backspace)
                                elif button.text == "Notepad":
                                    typingInNotepad = not typingInNotepad  # Toggle typing mode
                                    button.color = (128, 128, 128) if typingInNotepad else (255, 0, 255)  # Grey if active, purple if inactive
                                else:
                                    lastKeyPressTime = currentTime
                                    if typingInNotepad:
                                        keyboard.press(button.text)
                                        keyboard.release(button.text)
                                    else:
                                        finalText += button.text
                                    time.sleep(0.1)

        # Place the placeholder below the Notepad button row
        cv2.rectangle(img, (50, 100 * (len(keys) + 1)), (750, 100 * (len(keys) + 1) + 100), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, finalText, (60, 100 * (len(keys) + 1) + 60), cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255), 6)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
