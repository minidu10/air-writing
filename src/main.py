import argparse
import datetime as dt
import sys
import time
import cv2

from hand_tracker import HandTracker
from canvas import AirCanvas
from recognizer import Recognizer


WINDOW_NAME = "Air Writing"
RECOGNIZE_HOLD_FRAMES = 12  # ~0.4s at 30 FPS — avoids triggering on a flicker.
IDLE_AUTO_RECOGNIZE_SEC = 2.0  # auto-trigger after this long of pen-up with ink on canvas.
RECOGNIZE_COOLDOWN_SEC = 1.5


def draw_hud(frame, recognized_text, gesture, status):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.putText(
        frame,
        f"Text: {recognized_text}" if recognized_text else "Text: (write something)",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )
    cv2.putText(
        frame,
        f"Gesture: {gesture}  |  {status}",
        (10, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (200, 200, 200),
        1,
    )
    cv2.putText(
        frame,
        "Index = draw | Index+Middle = erase | Open palm = recognize | C clear | ESC quit",
        (10, h - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (180, 180, 180),
        1,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Air writing — webcam hand-gesture text input.")
    parser.add_argument(
        "--save",
        metavar="FILE",
        help="Append every recognized phrase to this file with a timestamp.",
    )
    parser.add_argument(
        "--backend",
        choices=("easyocr", "trocr"),
        default="easyocr",
        help="OCR backend. trocr is more accurate on handwriting but heavier (~1.4GB).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    save_fp = open(args.save, "a", encoding="utf-8") if args.save else None
    if save_fp:
        save_fp.write(f"\n--- session {dt.datetime.now().isoformat(timespec='seconds')} ---\n")
        save_fp.flush()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Could not open webcam.", file=sys.stderr)
        return 1

    ok, frame = cap.read()
    if not ok:
        print("Could not read first frame.", file=sys.stderr)
        cap.release()
        return 1
    h, w = frame.shape[:2]

    tracker = HandTracker()
    canvas = AirCanvas(h, w)

    print(f"Loading OCR backend: {args.backend} (first run downloads model weights)...")
    recognizer = Recognizer(backend=args.backend)
    print("Ready.")

    recognized_text = ""
    status = "ready"
    recognize_streak = 0
    last_recognize_at = 0.0
    last_drew_at = 0.0

    def run_recognition():
        nonlocal recognized_text, status, last_recognize_at
        status = "recognizing..."
        cv2.imshow(WINDOW_NAME, frame)
        cv2.waitKey(1)
        text = recognizer.recognize(canvas.get_image_for_ocr())
        if text:
            recognized_text = (recognized_text + " " + text).strip() if recognized_text else text
            status = f"recognized: {text}"
            if save_fp:
                save_fp.write(f"{dt.datetime.now().isoformat(timespec='seconds')}  {text}\n")
                save_fp.flush()
        else:
            status = "no text found"
        canvas.clear()
        last_recognize_at = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror so movement feels natural

        info = tracker.process(frame)
        gesture = info["gesture"]
        now = time.time()
        cooldown_over = now - last_recognize_at > RECOGNIZE_COOLDOWN_SEC

        if gesture == "pen_down":
            canvas.add_point(info["fingertip"], mode="draw")
            recognize_streak = 0
            last_drew_at = now
        elif gesture == "erase":
            canvas.add_point(info["fingertip"], mode="erase")
            recognize_streak = 0
            last_drew_at = now
        elif gesture == "recognize":
            canvas.pen_up()
            recognize_streak += 1
            if recognize_streak >= RECOGNIZE_HOLD_FRAMES and not canvas.is_empty() and cooldown_over:
                run_recognition()
                recognize_streak = 0
        else:
            canvas.pen_up()
            recognize_streak = 0
            # Auto-recognize when user pauses with ink on the canvas.
            if (
                not canvas.is_empty()
                and last_drew_at > 0
                and now - last_drew_at > IDLE_AUTO_RECOGNIZE_SEC
                and cooldown_over
            ):
                run_recognition()

        canvas.render(frame)
        tracker.draw_landmarks(frame, info["landmarks"])
        if info["fingertip"] is not None:
            if gesture == "pen_down":
                cv2.circle(frame, info["fingertip"], 8, (0, 255, 255), -1)
            elif gesture == "erase":
                cv2.circle(frame, info["fingertip"], 24, (0, 0, 255), 2)

        draw_hud(frame, recognized_text, gesture, status)
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        if key in (ord("c"), ord("C")):
            canvas.clear()
            status = "canvas cleared"
        if key in (ord("x"), ord("X")):
            recognized_text = ""
            status = "text buffer cleared"

    cap.release()
    cv2.destroyAllWindows()
    tracker.close()
    if save_fp:
        save_fp.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
