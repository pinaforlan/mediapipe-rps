import cv2
import mediapipe as mp
import numpy as np
import random
import math
import time
import os

# Optional TrueType font support via Pillow (installed automatically with MediaPipe)
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 1. Custom UI font helper
FONT_CACHE = {}

def get_windows_font(size):
    """Loads a clean Windows system font (Bahnschrift, Segoe UI Bold, or Arial Bold)."""
    if size in FONT_CACHE:
        return FONT_CACHE[size]
    
    font_candidates = [
        "C:/Windows/Fonts/bahnschrift.ttf",  # Sports broadcast style font
        "C:/Windows/Fonts/segoeuib.ttf",     # Segoe UI Bold
        "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold
        "C:/Windows/Fonts/consolab.ttf"      # Consolas Bold
    ]
    for path in font_candidates:
        if os.path.exists(path):
            FONT_CACHE[size] = ImageFont.truetype(path, size)
            return FONT_CACHE[size]
    return None

def draw_text(frame, text, pos, size=28, color=(255, 255, 255), center=False):
    """Draws crisp TrueType text with a drop shadow, or falls back to anti-aliased OpenCV font."""
    x, y = pos
    if PIL_AVAILABLE:
        font = get_windows_font(size)
        if font is not None:
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            
            if center:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                x = (frame.shape[1] - text_w) // 2

            # Convert BGR (OpenCV) to RGB (Pillow)
            rgb_color = (color[2], color[1], color[0])
            
            # Draw black drop shadow for readability
            draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
            draw.text((x, y), text, font=font, fill=rgb_color)
            
            frame[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            return

    # Fallback: OpenCV duplex font with anti-aliasing
    scale = size / 32.0
    if center:
        (text_w, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, 2)
        x = (frame.shape[1] - text_w) // 2
    cv2.putText(frame, text, (x + 2, y + 30), cv2.FONT_HERSHEY_DUPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y + 28), cv2.FONT_HERSHEY_DUPLEX, scale, color, 2, cv2.LINE_AA)

# 2. Initialising hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# 3. Classifying hand gestures
def classify_gesture(landmarks):
    finger_joints = [(8, 6), (12, 10), (16, 14), (20, 18)]
    wrist = landmarks[0]
    fingers_open = []

    for tip_id, pip_id in finger_joints:
        tip = landmarks[tip_id]
        pip = landmarks[pip_id]
        dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dist_pip = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
        fingers_open.append(dist_tip > dist_pip)

    if fingers_open == [False, False, False, False]:
        return "Rock"
    elif fingers_open == [True, True, True, True]:
        return "Paper"
    elif fingers_open == [True, True, False, False]:
        return "Scissors"
    else:
        return "Unknown"

# 4. Determining the winner
def get_winner(player, cpu):
    if player in ["Unknown", "No hand detected"]:
        return "Invalid move"
    if player == cpu:
        return "Draw!"
    if (player == "Rock" and cpu == "Scissors") or \
       (player == "Paper" and cpu == "Rock") or \
       (player == "Scissors" and cpu == "Paper"):
        return "You win!"
    else:
        return "CPU wins!"

# 5. Formatting the best-of-7 series
def get_series_banner(p_score, c_score):
    game_num = p_score + c_score + 1
    if p_score == 3 and c_score == 3:
        return "GAME 7 | SERIES TIED 3-3 | WIN OR GO HOME"
    elif p_score == c_score:
        return f"GAME {game_num} OF 7 | SERIES TIED {p_score}-{c_score}"
    elif p_score > c_score:
        return f"GAME {game_num} OF 7 | PLAYER LEADS {p_score}-{c_score}"
    else:
        return f"GAME {game_num} OF 7 | CPU LEADS {c_score}-{p_score}"

# 6. Game state variables
TARGET_WINS = 4
cap = cv2.VideoCapture(0)
player_score = 0
cpu_score = 0
state = "WAITING" # States: WAITING, COUNTDOWN, RESULT, SERIES_OVER
countdown_start = 0
cpu_choice = ""
locked_player_choice = ""
round_result = ""

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_gesture = "No hand detected"

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            current_gesture = classify_gesture(hand_lms.landmark)

    # --- Top Overlay ---
    cv2.rectangle(frame, (0, 0), (w, 95), (25, 25, 25), cv2.FILLED)
    cv2.line(frame, (0, 95), (w, 95), (0, 215, 255), 2)
    
    draw_text(frame, f"Player: {player_score}  |  CPU: {cpu_score}", (20, 10), size=28, color=(255, 255, 255))
    draw_text(frame, "[Q / ESC] Exit", (w - 175, 14), size=20, color=(180, 180, 180))
    draw_text(frame, f"Current gesture: {current_gesture}", (20, 50), size=24, color=(0, 255, 255))

    # --- State Machine ---
    if state == "WAITING":
        series_banner = get_series_banner(player_score, cpu_score)
        draw_text(frame, series_banner, (0, 180), size=26, color=(0, 215, 255), center=True)
        draw_text(frame, "Press Space to start", (0, 235), size=32, color=(255, 255, 0), center=True)

    elif state == "COUNTDOWN":
        series_banner = get_series_banner(player_score, cpu_score)
        draw_text(frame, series_banner, (0, 150), size=24, color=(0, 215, 255), center=True)
        
        elapsed = time.time() - countdown_start
        remaining = 3 - int(elapsed)
        if remaining > 0:
            draw_text(frame, f"Shoot in: {remaining}...", (0, 220), size=44, color=(0, 165, 255), center=True)
        else:
            locked_player_choice = current_gesture
            cpu_choice = random.choice(["Rock", "Paper", "Scissors"])
            round_result = get_winner(locked_player_choice, cpu_choice)

            if round_result == "You win!":
                player_score += 1
            elif round_result == "CPU wins!":
                cpu_score += 1

            # Check if someone won the series (4 wins)
            if player_score == TARGET_WINS or cpu_score == TARGET_WINS:
                state = "SERIES_OVER"
            else:
                state = "RESULT"

    elif state == "RESULT":
        series_banner = get_series_banner(player_score, cpu_score)
        draw_text(frame, series_banner, (0, 130), size=22, color=(0, 215, 255), center=True)
        draw_text(frame, f"You: {locked_player_choice}  |  CPU: {cpu_choice}", (0, 185), size=30, color=(255, 255, 255), center=True)
        
        res_color = (0, 255, 0) if "you win" in round_result else ((0, 0, 255) if "CPU wins" in round_result else (0, 215, 255))
        draw_text(frame, round_result, (0, 240), size=36, color=res_color, center=True)
        draw_text(frame, "Press Space for next game", (0, 310), size=26, color=(255, 255, 0), center=True)

    elif state == "SERIES_OVER":
        # Overlay for results
        overlay = frame.copy()
        cv2.rectangle(overlay, (30, 120), (w - 30, h - 40), (15, 15, 15), cv2.FILLED)
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)
        cv2.rectangle(frame, (30, 120), (w - 30, h - 40), (0, 215, 255), 2)

        total_games = player_score + cpu_score
        draw_text(frame, f"Final move — You: {locked_player_choice} | CPU: {cpu_choice}", (0, 140), size=22, color=(200, 200, 200), center=True)

        if player_score == TARGET_WINS:
            series_title = f"SERIES WINNER: YOU WIN 4-{cpu_score} (IN {total_games} GAMES)!"
            title_color = (0, 255, 0)
            sub_note = "CLEAN SWEEP!" if cpu_score == 0 else ("GAME 7 VICTORY!" if cpu_score == 3 else "SERIES CLINCHED!")
        else:
            series_title = f"SERIES OVER: CPU WINS 4-{player_score} (IN {total_games} GAMES)!"
            title_color = (0, 80, 255)
            sub_note = "SWEPT BY CPU!" if player_score == 0 else ("GAME 7 LOST!" if player_score == 3 else "SERIES LOST!")

        draw_text(frame, series_title, (0, 195), size=26, color=title_color, center=True)
        draw_text(frame, sub_note, (0, 240), size=30, color=(0, 215, 255), center=True)

        # Exit and replay prompts (displayed whether you win or lose)
        draw_text(frame, "Press [R] to play again", (0, 315), size=24, color=(255, 255, 255), center=True)
        draw_text(frame, "Press [Q] or [ESC] to exit", (0, 360), size=24, color=(100, 255, 255), center=True)

    cv2.imshow("pinaforlan's MediaPipe RPS project", frame)

    key = cv2.waitKey(1) & 0xFF
    # Exit anytime on 'q', 'Q', or ESC (27)
    if key in [ord('q'), ord('Q'), 27]:
        break
    # Advance round on SPACE
    elif key == ord(' ') and state in ["WAITING", "RESULT"]:
        state = "COUNTDOWN"
        countdown_start = time.time()
    # Restart series on 'r' or 'R' when series is over
    elif key in [ord('r'), ord('R')] and state == "SERIES_OVER":
        player_score = 0
        cpu_score = 0
        state = "COUNTDOWN"
        countdown_start = time.time()

cap.release()
cv2.destroyAllWindows()
