import cv2
import mediapipe as mp
import math
from pynput.keyboard import Controller
import time

# MediaPipe and Keyboard Setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7,
                      min_tracking_confidence=0.7)
mpdraw = mp.solutions.drawing_utils
keyboard = Controller()

# Camera Setup (Increased Window Size)
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Global Variables
text = ""
delay = 0
selected_button = None
shift = False  # Track shift key state
last_press_time = 0  # Track time of last key press

# Button Class
class Button():
    def __init__(self, pos, text, size=[85, 85], column=None):
        self.pos = pos
        self.size = size
        self.text = text
        self.column = column  # Track column for second column highlighting

# Keyboard Layout (Include numbers and symbols)
keys = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
bottom_keys = [["SP", "CL", "DEL", "SHIFT"]]  # Space, Clear, Delete, and Shift buttons

# Create Buttons
buttonList = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        buttonList.append(Button([100 * j + 20, 100 * i + 20], key, column=j))

# Add Bottom Buttons
for i, key in enumerate(bottom_keys[0]):
    buttonList.append(Button([250 * i + 20, 100 * len(keys) + 20], key, size=[240, 85]))

# Helper Functions
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def draw_button(img, button, selected=False, pressed=False):
    x, y = button.pos
    w, h = button.size

    # Button background with rounded corners
    if pressed:
        color = (0, 255, 0)  # Green when pressed
    elif selected:
        color = (0, 200, 255)  # Light blue when selected
    else:
        color = (255, 200, 0)  # Yellow by default

    # Draw rounded rectangle
    cv2.rectangle(img, (x, y), (x + w, y + h), color, -1, cv2.LINE_AA)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 2, cv2.LINE_AA)  # Border

    # Button text
    text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = x + (w - text_size[0]) // 2
    text_y = y + (h + text_size[1]) // 2
    cv2.putText(img, button.text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def drawAll(img, buttonList, selected=None, pressed=None):
    for button in buttonList:
        draw_button(img, button, selected=button == selected, pressed=button == pressed)
    return img

# Main Loop
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, (1280, 720))  # Resize to increased size
    frame = cv2.flip(frame, 1)
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    landmarks = []

    # Draw Buttons
    frame = drawAll(frame, buttonList, selected_button)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, _ = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append([id, cx, cy])

    if landmarks:
        try:
            # Index Finger (Selection)
            x8, y8 = landmarks[8][1], landmarks[8][2]
            # Middle Finger (Press)
            x12, y12 = landmarks[12][1], landmarks[12][2]

            # Check for selected button
            selected_button = None
            min_distance = float('inf')
            for button in buttonList:
                xb, yb = button.pos
                wb, hb = button.size
                distance = calculate_distance(x8, y8, xb + wb // 2, yb + hb // 2)
                if distance < min_distance:
                    min_distance = distance
                    selected_button = button

            # Check if middle finger is near the selected button
            if selected_button:
                xb, yb = selected_button.pos
                wb, hb = selected_button.size
                if xb < x12 < xb + wb and yb < y12 < yb + hb:
                    if delay == 0:
                        key = selected_button.text
                        if key == "SP":
                            text += " "
                            keyboard.press(" ")
                        elif key == "CL":
                            text = ""
                        elif key == "DEL":  # Delete last character
                            if time.time() - last_press_time > 0.5:  # Add delay for backspace
                                text = text[:-1]
                                keyboard.press("backspace")
                                last_press_time = time.time()
                        elif key == "SHIFT":  # Toggle shift key
                            shift = not shift
                        else:
                            if shift:
                                text += key.upper()
                                keyboard.press(key.upper())
                            else:
                                text += key.lower()
                                keyboard.press(key.lower())
                        delay = 1
        except Exception as e:
            print("Error:", e)

    if delay != 0:
        delay += 1
        if delay > 10:
            delay = 0

    # Display Typed Text with a clear, modern font and fit it within the screen
    cv2.rectangle(frame, (50, 580), (1230, 680), (255, 255, 255), -1)  # Background for text

    # Adjust font size based on the length of text to fit within the box
    font_scale = 2
    while cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 3)[0][0] > 1180:
        font_scale -= 0.1  # Decrease font size to fit text

    cv2.putText(frame, text, (60, 650), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 3)  # Black font for contrast

    # Save the text to a file
    with open("typed_text.txt", "w") as file:
        file.write(text)

    # Show Frame
    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()