import cv2
import mediapipe as mp
import random
import numpy as np
import time

# Initialize Mediapipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Load hand gesture images
rock_img = cv2.imread("Resources/1.png")
paper_img = cv2.imread("Resources/2.png")
scissors_img = cv2.imread("Resources/3.png")


# Resize images dynamically based on screen size
def resize_image(img, width, height):
    return cv2.resize(img, (width, height)) if img is not None else None


# Start webcam capture
cap = cv2.VideoCapture(0)

# Set up full-screen window
cv2.namedWindow("Rock-Paper-Scissors Game", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Rock-Paper-Scissors Game", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Game state
game_active = False
player_move = None
ai_move = None
result_text = ""


def get_hand_gesture(landmarks):
    """Determine the hand gesture based on finger positions"""
    if not landmarks:
        return None

    tip_ids = [4, 8, 12, 16, 20]
    fingers = []
    fingers.append(1 if landmarks[tip_ids[0]][0] < landmarks[tip_ids[0] - 1][0] else 0)
    for id in range(1, 5):
        fingers.append(1 if landmarks[tip_ids[id]][1] < landmarks[tip_ids[id] - 2][1] else 0)

    if fingers == [0, 0, 0, 0, 0]:
        return "rock"
    elif fingers == [0, 1, 1, 1, 1]:
        return "paper"
    elif fingers == [0, 1, 0, 0, 0]:
        return "scissors"
    return None


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Get screen resolution dynamically
    screen_width = 1920
    screen_height = 1080
    frame = cv2.resize(frame, (screen_width, screen_height))  # Resize frame to full-screen

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if not game_active:
        cv2.putText(frame, "Press 'S' to Start Game", (screen_width // 3, screen_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.imshow("Rock-Paper-Scissors Game", frame)
        key = cv2.waitKey(1)
        if key == ord('s'):
            game_active = True
        elif key == ord('q'):
            break
        continue

    player_move = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            lm_list = [[int(lm.x * w), int(lm.y * h)] for lm in hand_landmarks.landmark]
            player_move = get_hand_gesture(lm_list)

    if player_move:
        ai_move = random.choice(["rock", "paper", "scissors"])
        result_text = ""

        if player_move == ai_move:
            result_text = "It's a Tie!"
        elif (player_move == "rock" and ai_move == "scissors") or \
                (player_move == "paper" and ai_move == "rock") or \
                (player_move == "scissors" and ai_move == "paper"):
            result_text = "You Win!"
        else:
            result_text = "AI Wins!"

        # Display results in the center of the screen
        cv2.putText(frame, "Rock-Paper-Scissors", (screen_width // 4, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
        cv2.putText(frame, f"Your Move: {player_move}", (screen_width // 4, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
        cv2.putText(frame, f"AI Move: {ai_move}", (screen_width // 4, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
        cv2.putText(frame, result_text, (screen_width // 3, screen_height - 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 6)

        # Display images of player and AI moves
        rock_resized = resize_image(rock_img, 300, 300)
        paper_resized = resize_image(paper_img, 300, 300)
        scissors_resized = resize_image(scissors_img, 300, 300)

        if player_move == "rock" and rock_resized is not None:
            frame[300:600, 100:400] = rock_resized
        elif player_move == "paper" and paper_resized is not None:
            frame[300:600, 100:400] = paper_resized
        elif player_move == "scissors" and scissors_resized is not None:
            frame[300:600, 100:400] = scissors_resized

        if ai_move == "rock" and rock_resized is not None:
            frame[300:600, screen_width - 400:screen_width - 100] = rock_resized
        elif ai_move == "paper" and paper_resized is not None:
            frame[300:600, screen_width - 400:screen_width - 100] = paper_resized
        elif ai_move == "scissors" and scissors_resized is not None:
            frame[300:600, screen_width - 400:screen_width - 100] = scissors_resized

        cv2.imshow("Rock-Paper-Scissors Game", frame)
        cv2.waitKey(2000)

        # Play again prompt
        frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        cv2.putText(frame, "Play Again? (Press 'Y' to Continue or 'Q' to Quit)",
                    (screen_width // 6, screen_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
        cv2.imshow("Rock-Paper-Scissors Game", frame)
        key = cv2.waitKey(0)
        if key == ord('y'):
            game_active = True
        elif key == ord('q'):
            break

    cv2.imshow("Rock-Paper-Scissors Game", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
