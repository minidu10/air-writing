import os
import time
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


# MediaPipe hand landmark indices we care about.
WRIST = 0
THUMB_TIP = 4
INDEX_PIP = 6
INDEX_TIP = 8
MIDDLE_PIP = 10
MIDDLE_TIP = 12
RING_PIP = 14
RING_TIP = 16
PINKY_PIP = 18
PINKY_TIP = 20

# Connections between landmarks for drawing (mirrors mp.solutions.hands.HAND_CONNECTIONS).
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # middle
    (9, 13), (13, 14), (14, 15), (15, 16),   # ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17),                                  # palm base
)

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
DEFAULT_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models"
)
MODEL_FILENAME = "hand_landmarker.task"


def _ensure_model(model_dir=DEFAULT_MODEL_DIR):
    os.makedirs(model_dir, exist_ok=True)
    path = os.path.join(model_dir, MODEL_FILENAME)
    if not os.path.exists(path):
        print(f"Downloading hand landmarker model (~6 MB) to {path} ...")
        urllib.request.urlretrieve(MODEL_URL, path)
        print("Model downloaded.")
    return path


class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.5, tracking_confidence=0.5):
        model_path = _ensure_model()
        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self._start = time.time()

    def process(self, frame_bgr):
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts_ms = int((time.time() - self._start) * 1000)
        result = self.landmarker.detect_for_video(mp_image, ts_ms)

        info = {"fingertip": None, "gesture": "idle", "landmarks": None}
        if not result.hand_landmarks:
            return info

        hand = result.hand_landmarks[0]
        info["landmarks"] = hand
        tip = hand[INDEX_TIP]
        info["fingertip"] = (int(tip.x * w), int(tip.y * h))
        info["gesture"] = self._classify(hand)
        return info

    @staticmethod
    def draw_landmarks(frame_bgr, landmarks):
        if landmarks is None:
            return
        h, w = frame_bgr.shape[:2]
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame_bgr, pts[a], pts[b], (200, 200, 200), 2, cv2.LINE_AA)
        for p in pts:
            cv2.circle(frame_bgr, p, 4, (0, 255, 0), -1, cv2.LINE_AA)

    @staticmethod
    def _finger_extended(landmarks, tip_idx, pip_idx):
        # In image coords Y grows downward, so an extended finger has tip Y < pip Y.
        return landmarks[tip_idx].y < landmarks[pip_idx].y

    def _classify(self, landmarks):
        index_up = self._finger_extended(landmarks, INDEX_TIP, INDEX_PIP)
        middle_up = self._finger_extended(landmarks, MIDDLE_TIP, MIDDLE_PIP)
        ring_up = self._finger_extended(landmarks, RING_TIP, RING_PIP)
        pinky_up = self._finger_extended(landmarks, PINKY_TIP, PINKY_PIP)

        if index_up and middle_up and ring_up and pinky_up:
            return "recognize"
        if index_up and middle_up and not ring_up and not pinky_up:
            return "erase"
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "pen_down"
        return "idle"

    def close(self):
        self.landmarker.close()
