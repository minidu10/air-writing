# Air Writing — Hand Gesture Text Input

Write letters in the air with your finger; your webcam reads the trail and prints the recognized text on screen.

Built with Python + OpenCV + MediaPipe + EasyOCR. Runs locally on your machine.

## How it works

1. Webcam captures video.
2. MediaPipe Hands tracks 21 landmarks on your hand at ~30 FPS.
3. When you raise **only your index finger**, the fingertip becomes a pen and draws a white trail on a black canvas overlay.
4. When you show an **open palm (all 5 fingers up)**, the canvas is sent to EasyOCR.
5. Recognized text appears at the top of the window and the canvas clears for the next word.

## Requirements

- Python 3.10, 3.11, or 3.12
- A webcam
- Windows / macOS / Linux

## Install

```bash
git clone https://github.com/<your-user>/hand-gesture-writing-app.git
cd hand-gesture-writing-app
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

First run downloads EasyOCR model weights (~64 MB) — needs internet once.

## Run

```bash
python src/main.py
```

## Controls

| Action | Gesture / Key |
|--------|---------------|
| Draw | Index finger up, others curled |
| Pen up (move without drawing) | Fist or any pose other than index-only |
| Recognize current canvas | Open palm (hold ~0.4s) |
| Clear canvas | Press `C` |
| Clear recognized text | Press `X` |
| Quit | Press `ESC` |

## Tips for better recognition

- Write **block capitals** — EasyOCR was trained on print, not cursive.
- Make letters **large** (fill most of the frame).
- Move slowly and steadily.
- Black background behind your hand helps a lot.
- Good lighting on your hand helps MediaPipe lock on.

## Project layout

```
src/
  main.py           # webcam loop + UI overlay
  hand_tracker.py   # MediaPipe wrapper + gesture classification
  canvas.py         # stroke buffer + drawing
  recognizer.py     # EasyOCR wrapper
requirements.txt
```

## Roadmap

- [ ] Replace EasyOCR with TrOCR (HuggingFace) for higher accuracy on handwriting
- [ ] Pinch gesture to toggle eraser
- [ ] Multi-stroke buffering (currently each open-palm recognizes the whole canvas)
- [ ] Save recognized sessions to a `.txt` file
- [ ] Demo GIF

## License

MIT — see [LICENSE](LICENSE).
