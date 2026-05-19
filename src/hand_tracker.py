import cv2
import mediapipe as mp


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


class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def process(self, frame_bgr):
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = self.hands.process(rgb)

        info = {"fingertip": None, "gesture": "idle", "landmarks": None}
        if not result.multi_hand_landmarks:
            return info

        hand = result.multi_hand_landmarks[0]
        info["landmarks"] = hand

        tip = hand.landmark[INDEX_TIP]
        info["fingertip"] = (int(tip.x * w), int(tip.y * h))
        info["gesture"] = self._classify(hand)
        return info

    def draw_landmarks(self, frame_bgr, landmarks):
        if landmarks is None:
            return
        self.mp_draw.draw_landmarks(
            frame_bgr,
            landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_styles.get_default_hand_landmarks_style(),
            self.mp_styles.get_default_hand_connections_style(),
        )

    @staticmethod
    def _finger_extended(landmarks, tip_idx, pip_idx):
        # In image coords Y grows downward, so an extended finger has tip Y < pip Y.
        return landmarks.landmark[tip_idx].y < landmarks.landmark[pip_idx].y

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
        self.hands.close()
