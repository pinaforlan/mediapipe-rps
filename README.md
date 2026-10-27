# mediapipe-rps
Inspired by the AKB48 Janken Tournament, this is a Python and MediaPipe-based rock-paper-scissors game with a best-of-7 structure and mildly-refined UI.

## Setting up
- First and foremost, install Python 3.11 (this game was built upon Python 3.11.9) - some say it's the easiest among all steps and they aren't lying.
(remember to "Add python.exe to PATH" when installation begins and find lines containing "Python" at System Properties\Advanced\Environment Variables\Path once it's done)
- Create a folder called __mediapipe-rps__ within your documents, then download the repo (which includes the __requirements.txt__ file) as a zip (or clone it if you already have Git: __git clone https://github.com/pinaforlan/mediapipe-rps__) and put its contents in said folder.
- Open your terminal/cmd and set up a virtual environment using (preferably) __python -m venv C:\Users\[You]\Documents\mediapipe-rps\.venv__, then __C:\Users\[You]\Documents\mediapipe-rps\.venv\Scripts\Activate.ps1__ (or __Activate.bat__ if you're on your cmd).
(for Mac and Linux users: __python3 -m venv /home/username/Documents/mediapipe-rps/.venv__, then __source /home/username/Documents/mediapipe-rps/.venv/bin/activate__)
- Run __pip install "mediapipe==0.10.21" "numpy<2.0.0" "opencv-python<5.0.0"__ (as seen on __requirements.txt__)...
(for best results, update pip to the latest version before that, though not recommended: __py -m pip install --upgrade pip__)
- ...and then __python rps_game.py__ to get the damn thing going (again from your terminal - it's best to clear it first) - it'll automatically pair with your webcam and activate it.
- Follow the game's instructions and try your best to clinch the series!

## Game mechanics
- Just like regular rock-paper-scissors, make the right hand gestures for the camera to register them.
- The game operates on an NBA-like best-of-7 series structure as its idol origin dictated:
  + First to 4 wins either by 4-0 (in 4), 4-1 (in 5), 4-2 (in 6) or 4-3 (in 7).
  + Game 7 puts you in a win-or-go-home situation.
- Press Space to progress onto the next round. There's also an exit prompt using either the Q or Esc keys.

## Project structure
```
mediapipe-rps
├── .gitignore                          # Directs Git to ignore specific local files (if you have it)
├── 26521213 - Báo cáo MediaPipe.pdf    # Report on this project (to be added)
├── demo-link.txt                       # Link to demonstration video (to be added)
├── rps-game.py                         # The entire game
└── requirements.txt                    # Dependency requirements
```

(I probably need test pipelines too)
