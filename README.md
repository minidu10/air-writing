# Air Writing — Hand Gesture Text Input

Write letters in the air with your finger; your webcam reads the trail and prints the recognized text on screen.

Built with Python + OpenCV + MediaPipe + EasyOCR (or TrOCR). Runs locally on your machine.

## Demo

![demo](docs/demo.gif)

> Replace `docs/demo.gif` with your own recording — see [Recording a demo GIF](#recording-a-demo-gif) below.

## How it works

1. Webcam captures video.
2. MediaPipe Hands tracks 21 landmarks on your hand at ~30 FPS.
3. When you raise **only your index finger**, the fingertip becomes a pen and draws a white trail on a black canvas overlay.
4. When you show an **open palm (all 5 fingers up)** OR pause for 2 seconds, the canvas is sent to the OCR backend.
5. Recognized text appears at the top of the window and the canvas clears for the next word.
6. Raise **index + middle finger (peace sign)** to erase.

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

First run of EasyOCR downloads model weights (~64 MB) — needs internet once.

### Optional: TrOCR backend (more accurate handwriting recognition)

EasyOCR is trained on printed text and works on neat block letters. **TrOCR** (Microsoft) is trained on actual handwriting and is much more forgiving — at the cost of a ~1.4 GB model and slower inference.

```bash
pip install -r requirements-trocr.txt
python src/main.py --backend trocr
```

## Run

```bash
python src/main.py                        # default: EasyOCR
python src/main.py --backend trocr        # use TrOCR
python src/main.py --save session.txt     # append recognized text to a file
python src/main.py --backend trocr --save session.txt
```

### Desktop shortcut (Windows)

Double-click to launch — no terminal required.

```powershell
powershell -ExecutionPolicy Bypass -File install_shortcut.ps1
```

This creates two icons on your Desktop:

- **Air Writing** — launches with a minimized console window (useful for the first run so you can see errors).
- **Air Writing (silent)** — runs the app with no console at all (clean experience once you've confirmed it works).

The shortcuts use [launch.bat](launch.bat), which auto-activates `.venv` if present and falls back to system Python otherwise. Re-run the installer any time to refresh the shortcuts.

## Controls

| Action | Gesture / Key |
|--------|---------------|
| Draw | Index finger up, others curled |
| Erase | Index + middle finger up (peace sign) |
| Pen up (no draw) | Fist or any pose other than above |
| Recognize current canvas | Open palm (hold ~0.4s) **OR** stop drawing for 2s |
| Clear canvas | Press `C` |
| Clear recognized text | Press `X` |
| Quit | Press `ESC` |

## Saving sessions

Pass `--save <file>`. Every recognized phrase is appended with a timestamp:

```
--- session 2026-05-19T14:32:08 ---
2026-05-19T14:32:21  HELLO
2026-05-19T14:32:45  WORLD
```

## Tips for better recognition

- Write **block capitals** — EasyOCR was trained on print. TrOCR handles cursive better.
- Make letters **large** (fill most of the frame).
- Move slowly and steadily.
- Good lighting on your hand helps MediaPipe lock on.
- If recognition is poor with EasyOCR, switch to TrOCR.

## Recording a demo GIF

The README references `docs/demo.gif`. To record your own:

1. Create the folder: `mkdir docs` (or `New-Item -ItemType Directory docs` on Windows).
2. Run the app: `python src/main.py`.
3. Use [ScreenToGif](https://www.screentogif.com/) (Windows) or [Peek](https://github.com/phw/peek) (Linux) to capture the window.
4. Trim to 5–10 seconds, export as `docs/demo.gif`, then `git add docs/demo.gif && git commit -m "docs: add demo gif"`.

## Project layout

```
src/
  main.py           # webcam loop + UI overlay + CLI args
  hand_tracker.py   # MediaPipe wrapper + gesture classification
  canvas.py         # stroke buffer + drawing + erase
  recognizer.py     # OCR backends: EasyOCR (default) and TrOCR
requirements.txt
requirements-trocr.txt
```

## Roadmap

- [x] Eraser mode via two-finger gesture
- [x] Auto-recognize after 2s of pen-up idle
- [x] Save recognized text to a session file
- [x] TrOCR backend option
- [ ] Multi-stroke buffering across recognitions
- [ ] Color picker via finger position
- [ ] Demo GIF (record your own — see above)

## License

MIT — see [LICENSE](LICENSE).
