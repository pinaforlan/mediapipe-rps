import cv2
import mediapipe as mp
import random
import math
import time

# 1. Initialising hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# 2. Classifying hand gestures
def classify_gesture(landmarks):
    # Finger pairs: (Tip Landmark ID, Pip Knuckle Landmark ID)
    finger_joints = [(8, 6), (12, 10), (16, 14), (20, 18)]
    wrist = landmarks[0]
    fingers_open = []

    for tip_id, pip_id in finger_joints:
        tip = landmarks[tip_id]
        pip = landmarks[pip_id]

        # Calculate Euclidean distance from wrist (Landmark 0)
        dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dist_pip = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
        
        # Finger is extended if tip is further from wrist than the knuckle
        fingers_open.append(dist_tip > dist_pip)

    # Classification logic
    if fingers_open == [False, False, False, False]:
        return "Rock"
    elif fingers_open == [True, True, True, True]:
        return "Paper"
    elif fingers_open == [True, True, False, False]:
        return "Scissors"
    else:
        return "Unknown"

# 3. Determining the winner
def get_winner(player, cpu):
    if player == "Unknown":
        return "Invalid move"
    if player == cpu:
        return "Draw"
    if (player == "Rock" and cpu == "Scissors") or \
       (player == "Paper" and cpu == "Rock") or \
       (player == "Scissors" and cpu == "Paper"):
        return "Congrats, you win!"
    else:
        return "You lost, try again!"

# 4. Game state variables
cap = cv2.VideoCapture(0)
player_score = 0
cpu_score = 0
state = "WAITING" # States: WAITING, COUNTDOWN, RESULT
countdown_start = 0
cpu_choice = ""
locked_player_choice = ""
round_result = ""

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_gesture = "No hand detected"

    # Extract hand landmarks and run classification
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            current_gesture = classify_gesture(hand_lms.landmark)

    # Game state machine goes here
    if state == "WAITING":
        cv2.putText(frame, "Press Space to play", (140, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    elif state == "COUNTDOWN":
        elapsed = time.time() - countdown_start
        remaining = 3 - int(elapsed)
        if remaining > 0:
            cv2.putText(frame, f"Shoot in: {remaining}...", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)
        else:
            # Lock moves and evaluate winner
            locked_player_choice = current_gesture
            cpu_choice = random.choice(["Rock", "Paper", "Scissors"])
            round_result = get_winner(locked_player_choice, cpu_choice)

            if round_result == "Congrats, you win!":
                player_score += 1
            elif round_result == "You lost, try again!":
                cpu_score += 1

            state = "RESULT"

    elif state == "RESULT":
        cv2.putText(frame, f"You: {locked_player_choice} | CPU: {cpu_choice}", (80, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, round_result, (160, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3)
        cv2.putText(frame, "Press Space for next round", (120, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    # HUD overlay (score and live gesture preview)
    cv2.rectangle(frame, (0, 0), (640, 80), (30, 30, 30), cv2.FILLED)
    cv2.putText(frame, f"Player: {player_score}  |  CPU: {cpu_score}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"Current gesture: {current_gesture}", (20, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("pinaforlan's MediaPipe RPS project", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' ') and state in ["WAITING", "RESULT"]:
        state = "COUNTDOWN"
        countdown_start = time.time()

cap.release()
cv2.destroyAllWindows()